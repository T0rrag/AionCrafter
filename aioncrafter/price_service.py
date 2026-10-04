"""Nonblocking, single-owner request coordination; no real transport or sleeps.

Call resolve again at retry_at. A future adapter must enforce its own I/O timeout
and cancellation. Limits are caller-supplied policy, never inferred provider quotas.
"""
from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from .codec import ValidationError, require, validate_fields
from .identity import PriceIdentity
from .models import PriceObservation, PriceType, RightsStatus, timestamp
from .price_cache import PriceCache, PriceView, aware_now, duration


class ProviderFailure(Exception):
    def __init__(self, code: str, *, retryable: bool, retry_after: timedelta | None = None):
        require(code in ('throttled', 'timeout', 'unavailable', 'denied', 'invalid_response'), 'PROVIDER_ERROR', 'Use a normalized error code')
        require(type(retryable) is bool, 'TYPE', 'retryable must be boolean')
        if retry_after is not None:
            duration(retry_after, 'retry_after')
        self.code, self.retryable, self.retry_after = code, retryable, retry_after
        super().__init__(code)


@dataclass(frozen=True)
class RequestPolicy:
    batch_size: int
    requests_per_window: int
    window: timedelta
    max_attempts: int
    backoff: timedelta
    max_backoff: timedelta
    failure_cooldown: timedelta

    def __post_init__(self):
        validate_fields(self)
        require(self.batch_size > 0 and self.requests_per_window > 0 and self.max_attempts > 0,
                'POLICY', 'Batch, quota and attempt limits must be positive integers')
        for name in ('window', 'backoff', 'max_backoff', 'failure_cooldown'):
            duration(getattr(self, name), name)
            require(getattr(self, name) > timedelta(0), 'POLICY', 'Scheduling intervals must be positive')
        require(self.max_backoff >= self.backoff, 'POLICY', 'Backoff cap must cover initial delay')


@dataclass(frozen=True)
class PriceResolution:
    identity: PriceIdentity
    view: PriceView | None
    manual: PriceObservation | None
    origin: str
    state: str
    error: str | None
    retry_at: datetime | None

    @property
    def observations(self) -> tuple[PriceObservation, ...]:
        return (self.manual,) if self.manual is not None else (() if self.view is None else self.view.entry.observations)


class PriceService:
    def __init__(self, cache: PriceCache, policy: RequestPolicy, *, batched: bool = False):
        require(type(batched) is bool, 'TYPE', 'Batch support must be explicitly selected')
        require(not batched or callable(getattr(cache.provider, 'observations_for_batch', None)),
                'BATCH', 'Provider lacks the batch contract')
        self.cache, self.policy, self.batched = cache, policy, batched
        self._window_start = aware_now(cache.clock)
        self._requests = 0
        self._blocked_until = self._window_start
        self._attempts: dict[PriceIdentity, int] = {}
        self._errors: dict[PriceIdentity, str] = {}
        self._exhausted: set[PriceIdentity] = set()

    def reset_failures(self) -> None:
        """Explicit operator reset; does not bypass quota or provider cooldown."""
        self._attempts.clear()
        self._errors.clear()
        self._exhausted.clear()

    def _result(self, identity, *, error=None, retry_at=None, manual=None, cache_hit=True):
        view = self.cache.peek(identity)
        if view is not None:
            view = replace(view, cache_hit=cache_hit)
        if manual is not None:
            return PriceResolution(identity, view, manual, 'manual', 'manual', None, None)
        if error:
            state = 'stale_error' if view is not None and view.entry.observations else 'error'
        elif view is None or not view.entry.observations:
            state = 'missing'
        elif all(o.unit_price is None for o in view.entry.observations):
            state = 'unavailable'
        elif view.cache_expired or 'stale' in view.freshness or 'future' in view.freshness:
            state = 'stale'
        elif 'unknown' in view.freshness:
            state = 'unknown_age'
        elif any(o.unit_price is None for o in view.entry.observations):
            state = 'partial'
        else:
            state = 'fresh'
        return PriceResolution(identity, view, None, 'provider', state, error, retry_at)

    def _ready_at(self, now):
        # A clock rollback cannot reset quotas or bypass provider backoff.
        if now >= self._window_start + self.policy.window:
            self._window_start, self._requests = now, 0
        ready = self._blocked_until
        if now < self._window_start or self._requests >= self.policy.requests_per_window:
            ready = max(ready, self._window_start + self.policy.window)
        return ready

    def resolve(self, identities: tuple[PriceIdentity, ...], *, refresh: bool = False,
                manual: dict[PriceIdentity, PriceObservation] | None = None) -> tuple[PriceResolution, ...]:
        require(type(identities) is tuple and all(type(i) is PriceIdentity for i in identities),
                'TYPE', 'Expected a tuple of price identities')
        unique = tuple(dict.fromkeys(identities))
        manual = {} if manual is None else manual
        require(type(manual) is dict and set(manual) <= set(unique), 'OVERRIDE', 'Override must belong to this request')
        # Validate every override before transport or cache mutation.
        now = aware_now(self.cache.clock)
        for identity in unique:
            self.cache.check_identity(identity)
            if identity in manual:
                obs = manual[identity]
                require(type(obs) is PriceObservation and obs.identity == identity and obs.price_type is PriceType.MANUAL,
                        'OVERRIDE', 'Manual fallback requires a scoped manual observation')
                require(obs.provenance.rights_status is not RightsStatus.UNVERIFIED and timestamp(obs.fetched_at) <= now,
                        'OVERRIDE', 'Fallback needs valid rights and ingestion time')
        # Reserve manual IDs against all provider/manual history, not just the current
        # entry. This is atomic across the request and leaves cached prices untouched.
        self.cache.remember_observations(tuple(manual.values()))
        results, pending = {}, []
        for identity in unique:
            view = self.cache.peek(identity)
            if identity in manual:
                results[identity] = self._result(identity, manual=manual[identity])
            elif view and not view.cache_expired and not refresh and identity not in self._errors:
                results[identity] = self._result(identity)
            elif identity in self._exhausted:
                results[identity] = self._result(identity, error=self._errors[identity])
            else:
                pending.append(identity)
        size = self.policy.batch_size if self.batched else 1
        for start in range(0, len(pending), size):
            batch = tuple(pending[start:start + size])
            now = aware_now(self.cache.clock)
            ready = self._ready_at(now)
            if ready > now:
                for identity in batch:
                    results[identity] = self._result(identity, error=self._errors.get(identity, 'deferred'), retry_at=ready)
                continue
            self._requests += 1  # Every actual attempt, including failures, consumes quota.
            for identity in batch:
                self._attempts[identity] = self._attempts.get(identity, 0) + 1
            failure = None
            try:
                if self.batched:
                    response = self.cache.provider.observations_for_batch(batch)
                else:
                    response = {batch[0]: self.cache.provider.observations_for(batch[0])}
                require(type(response) is dict and set(response) == set(batch),
                        'BATCH', 'Response must cover exactly the requested identities')
                self.cache.store_batch(response)
            except ProviderFailure as exc:
                failure = exc
            except TimeoutError:
                failure = ProviderFailure('timeout', retryable=True)
            except ValidationError:
                failure = ProviderFailure('invalid_response', retryable=False)
            if failure is not None:
                now = aware_now(self.cache.clock)
                exhausted = {i for i in batch if not failure.retryable or self._attempts[i] >= self.policy.max_attempts}
                delay = self.policy.backoff
                # Saturating doubling avoids huge powers or timedelta overflow.
                for _ in range(max(self._attempts[i] for i in batch) - 1):
                    delay = min(delay, self.policy.max_backoff - delay) + delay
                    if delay >= self.policy.max_backoff:
                        break
                delay = max(delay, failure.retry_after or timedelta(0))
                if exhausted:
                    self._exhausted.update(exhausted)
                    delay = max(delay, self.policy.failure_cooldown)
                self._blocked_until = max(self._blocked_until, now + delay)
                for identity in batch:
                    self._errors[identity] = failure.code
                    results[identity] = self._result(identity, error=failure.code,
                                                     retry_at=None if identity in exhausted else self._ready_at(now))
            else:
                for identity in batch:
                    self._attempts.pop(identity, None)
                    self._errors.pop(identity, None)
                    results[identity] = self._result(identity, cache_hit=False)
        return tuple(results[i] for i in unique)
