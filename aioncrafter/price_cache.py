"""Provider-independent in-memory cache. No provider is connected by this module."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

from .codec import require
from .identity import PriceIdentity
from .models import PriceObservation, RightsStatus, timestamp
from .providers import PriceProvider


def aware_now(clock: Callable[[], datetime]) -> datetime:
    now = clock()
    require(isinstance(now, datetime) and now.tzinfo is not None and now.utcoffset() is not None,
            'CLOCK', 'Clock must return a timezone-aware datetime')
    return now


def duration(value: timedelta, name: str) -> None:
    require(type(value) is timedelta and value >= timedelta(0), 'DURATION', f'{name} must be nonnegative')


@dataclass(frozen=True)
class CachedPrices:
    identity: PriceIdentity
    observations: tuple[PriceObservation, ...]
    retrieved_at: datetime


@dataclass(frozen=True)
class PriceView:
    entry: CachedPrices
    cache_hit: bool
    cache_expired: bool
    # Parallel to observations: fresh/stale/unknown/future. Empty is missing, not zero.
    freshness: tuple[str, ...]


class PriceCache:
    """Single-owner cache; TTL controls transport, source age controls freshness.

    Observation records are retained verbatim, including their original fetched_at.
    retrieved_at describes our transport, never the age of a price. A provider-scoped
    ID registry rejects altered replay during this cache's lifetime. Persistent history
    remains the responsibility of the existing observation store.
    """

    def __init__(self, provider: PriceProvider, *, clock: Callable[[], datetime],
                 ttl: timedelta, max_source_age: timedelta):
        duration(ttl, 'ttl')
        duration(max_source_age, 'max_source_age')
        self.provider = provider
        self.capabilities = provider.capabilities
        self.clock = clock
        self.ttl = ttl
        self.max_source_age = max_source_age
        self._entries: dict[PriceIdentity, CachedPrices] = {}
        self._ids: dict[str, PriceObservation] = {}

    def check_identity(self, identity: PriceIdentity) -> None:
        require(type(identity) is PriceIdentity, 'TYPE', 'Expected PriceIdentity')
        require(identity.market in self.capabilities.scopes, 'SCOPE_MISMATCH', 'Provider does not cover this market')
        require(self.provider.capabilities == self.capabilities, 'CAPABILITIES', 'Provider capabilities changed; create a new cache')

    def view(self, entry: CachedPrices, *, cache_hit: bool) -> PriceView:
        now = aware_now(self.clock)
        age = now - entry.retrieved_at
        states = []
        for obs in entry.observations:
            source_age = None if obs.observed_at is None else now - timestamp(obs.observed_at)
            states.append('unknown' if source_age is None else 'future' if source_age < timedelta(0)
                          else 'stale' if source_age > self.max_source_age else 'fresh')
        return PriceView(entry, cache_hit, age < timedelta(0) or age >= self.ttl, tuple(states))

    def peek(self, identity: PriceIdentity) -> PriceView | None:
        self.check_identity(identity)
        entry = self._entries.get(identity)
        return None if entry is None else self.view(entry, cache_hit=True)

    def _validated_ids(self, observations: tuple[PriceObservation, ...], now: datetime) -> dict[str, PriceObservation]:
        require(type(observations) is tuple and all(type(x) is PriceObservation for x in observations),
                'TYPE', 'Expected an observation tuple')
        pending_ids = {}
        for obs in observations:
            self.check_identity(obs.identity)
            require(obs.provenance.rights_status is not RightsStatus.UNVERIFIED,
                    'RIGHTS', 'Unverified observations cannot enter the cache')
            require(timestamp(obs.fetched_at) <= now, 'TIMESTAMP', 'Observation ingestion is in the future')
            require(obs.observation_id not in pending_ids, 'DUPLICATE_ID', 'Response repeats an observation ID')
            prior = self._ids.get(obs.observation_id)
            require(prior is None or prior == obs, 'IMMUTABLE_ID', 'Changed observation needs a new ID')
            pending_ids[obs.observation_id] = obs
        return pending_ids

    def remember_observations(self, observations: tuple[PriceObservation, ...]) -> None:
        """Atomically reserve immutable IDs without replacing provider cache entries.

        Manual selections share the same ID history as provider responses. A rejected
        selection reserves nothing; a valid replay is idempotent for this cache lifetime.
        """
        self._ids.update(self._validated_ids(observations, aware_now(self.clock)))

    def store_batch(self, responses: dict[PriceIdentity, tuple[PriceObservation, ...]]) -> None:
        """Validate a whole response before committing any entries or ID registrations."""
        require(type(responses) is dict, 'TYPE', 'Expected a response mapping')
        now = aware_now(self.clock)
        pending_entries = {}
        records = []
        for identity, observations in responses.items():
            self.check_identity(identity)
            require(type(observations) is tuple and all(type(x) is PriceObservation for x in observations),
                    'TYPE', 'Provider must return an observation tuple')
            for obs in observations:
                require(obs.identity == identity, 'SCOPE_MISMATCH', 'Response identity differs from request')
            records.extend(observations)
            pending_entries[identity] = CachedPrices(identity, observations, now)
        pending_ids = self._validated_ids(tuple(records), now)
        self._ids.update(pending_ids)
        self._entries.update(pending_entries)

    def get(self, identity: PriceIdentity, *, refresh: bool = False) -> PriceView:
        prior = self.peek(identity)
        if prior is not None and not prior.cache_expired and not refresh:
            return prior
        observations = self.provider.observations_for(identity)
        self.store_batch({identity: observations})
        return self.view(self._entries[identity], cache_hit=False)
