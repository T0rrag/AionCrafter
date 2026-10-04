from dataclasses import replace
from datetime import timedelta
import unittest

from aioncrafter.codec import ValidationError
from aioncrafter.price_cache import PriceCache
from aioncrafter.price_service import PriceService, ProviderFailure, RequestPolicy
from .synthetic_prices import Clock, SyntheticProvider, sample


class PriceServiceTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.obs = sample()
        self.identity = self.obs.identity
        self.provider = SyntheticProvider((self.obs,))
        self.cache = PriceCache(self.provider, clock=self.clock, ttl=timedelta(seconds=30),
                                max_source_age=timedelta(minutes=30))
        # Fictional test policies, not provider limits.
        self.policy = RequestPolicy(2, 10, timedelta(seconds=60), 3, timedelta(seconds=2),
                                    timedelta(seconds=5), timedelta(seconds=20))
        self.service = PriceService(self.cache, self.policy, batched=True)

    def resolve(self, **kwargs):
        return self.service.resolve((self.identity,), **kwargs)[0]

    def test_bounded_retry_schedule_and_no_sleep(self):
        self.provider.failures = [ProviderFailure('unavailable', retryable=True)] * 3
        first = self.resolve()
        self.assertEqual(first.retry_at, self.clock() + timedelta(seconds=2))
        self.assertEqual(self.resolve().retry_at, first.retry_at)
        self.assertEqual(len(self.provider.calls), 1)
        self.clock.advance(2)
        self.assertEqual(self.resolve().retry_at, self.clock() + timedelta(seconds=4))
        self.clock.advance(4)
        self.assertIsNone(self.resolve().retry_at)
        self.clock.advance(100)
        self.assertEqual(self.resolve().error, 'unavailable')
        self.assertEqual(len(self.provider.calls), 3)
        self.service.reset_failures()
        self.assertIsNone(self.resolve().error)

    def test_throttle_retry_after_is_not_shortened_by_backoff_cap(self):
        self.provider.failures = [ProviderFailure('throttled', retryable=True, retry_after=timedelta(seconds=90))]
        first = self.resolve()
        self.clock.advance(60)
        self.assertEqual(self.resolve().retry_at, first.retry_at)
        self.assertEqual(len(self.provider.calls), 1)
        self.clock.advance(30)
        self.assertIsNone(self.resolve().error)

    def test_exponential_delay_saturates_at_cap(self):
        self.service = PriceService(self.cache, replace(self.policy, max_attempts=5), batched=True)
        self.provider.failures = [ProviderFailure('timeout', retryable=True)] * 4
        for seconds in (2, 4, 5, 5):
            self.assertEqual(self.resolve().retry_at, self.clock() + timedelta(seconds=seconds))
            self.clock.advance(seconds)

    def test_failure_keeps_original_stale_price_and_provenance(self):
        self.resolve()
        self.clock.advance(30)
        self.provider.failures = [TimeoutError()]
        result = self.resolve()
        self.assertEqual((result.state, result.error), ('stale_error', 'timeout'))
        self.assertEqual(result.observations, (self.obs,))
        self.assertEqual(result.view.freshness, ('stale',))

    def test_deduplication_batches_and_partial_request_quota(self):
        self.service = PriceService(self.cache, replace(self.policy, requests_per_window=1), batched=True)
        ids = tuple(replace(self.identity, item=replace(self.identity.item, item_id=str(i))) for i in range(3))
        results = self.service.resolve(ids + (ids[0],))
        self.assertEqual(len(results), 3)
        self.assertEqual(self.provider.calls, [ids[:2]])
        self.assertEqual(results[-1].retry_at, self.clock() + timedelta(seconds=60))
        self.clock.advance(60)
        self.service.resolve((ids[-1],))
        self.assertEqual(len(self.provider.calls), 2)

    def test_failed_attempt_consumes_quota(self):
        self.service = PriceService(self.cache, replace(self.policy, requests_per_window=1))
        self.provider.failures = [ProviderFailure('timeout', retryable=True)]
        self.resolve()
        self.clock.advance(2)
        result = self.resolve()
        self.assertEqual(result.retry_at, self.clock() + timedelta(seconds=58))
        self.assertEqual(len(self.provider.calls), 1)

    def test_single_request_provider_does_not_assume_batch_support(self):
        self.service = PriceService(self.cache, self.policy)
        other = replace(self.identity, item=replace(self.identity.item, item_id='other'))
        self.service.resolve((self.identity, other))
        self.assertEqual(self.provider.calls, [(self.identity,), (other,)])

    def test_permanent_error_stops_batch_storm_and_reset_keeps_cooldown(self):
        self.provider.failures = [ProviderFailure('denied', retryable=False)]
        other = replace(self.identity, item=replace(self.identity.item, item_id='other'))
        self.service = PriceService(self.cache, self.policy)
        results = self.service.resolve((self.identity, other))
        self.assertEqual(len(self.provider.calls), 1)
        self.assertEqual(results[0].error, 'denied')
        self.assertEqual(results[1].error, 'deferred')
        self.service.reset_failures()
        self.resolve()
        self.assertEqual(len(self.provider.calls), 1)

    def test_manual_override_is_explicit_and_does_not_change_cache(self):
        self.resolve()
        override = replace(self.obs, observation_id='SYNTHETIC-manual', unit_price='0.00',
                           supersedes_id=self.obs.observation_id)
        result = self.resolve(manual={self.identity: override}, refresh=True)
        self.assertEqual((result.origin, result.state), ('manual', 'manual'))
        self.assertEqual(result.observations, (override,))
        self.assertEqual(result.view.entry.observations, (self.obs,))
        self.assertEqual(len(self.provider.calls), 1)
        self.assertEqual(self.resolve().origin, 'provider')

    def test_invalid_manual_override_is_rejected_before_transport(self):
        other = replace(self.identity, item=replace(self.identity.item, item_id='other'))
        with self.assertRaises(ValidationError):
            self.resolve(manual={self.identity: replace(self.obs, identity=other)})
        self.assertEqual(self.provider.calls, [])

    def test_incomplete_batch_does_not_replace_any_cached_record(self):
        self.resolve()
        other = replace(self.identity, item=replace(self.identity.item, item_id='other'))
        self.provider.observations_for_batch = lambda batch: {self.identity: ()}
        results = self.service.resolve((self.identity, other), refresh=True)
        self.assertTrue(all(r.error == 'invalid_response' for r in results))
        self.assertEqual(self.cache.peek(self.identity).entry.observations, (self.obs,))
        self.assertIsNone(self.cache.peek(other))

    def test_new_empty_response_clears_old_listing_without_zero_price(self):
        self.resolve()
        self.provider.responses.clear()
        result = self.resolve(refresh=True)
        self.assertEqual((result.state, result.observations), ('missing', ()))

    def test_unknown_and_unavailable_statuses(self):
        self.provider.responses[self.identity] = (replace(self.obs, observed_at=None),)
        self.assertEqual(self.resolve().state, 'unknown_age')
        self.provider.responses[self.identity] = (replace(self.obs, observation_id='missing', unit_price=None),)
        self.assertEqual(self.resolve(refresh=True).state, 'unavailable')

    def test_clock_rollback_cannot_reset_quota(self):
        self.resolve()
        self.clock.advance(-1)
        self.assertEqual(self.resolve(refresh=True).error, 'deferred')
        self.assertEqual(len(self.provider.calls), 1)

    def test_bad_configuration(self):
        for changes in ({'batch_size': True}, {'max_attempts': 0}, {'backoff': timedelta(0)},
                        {'max_backoff': timedelta(seconds=1)}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                replace(self.policy, **changes)

    def test_forced_refresh_failure_keeps_retry_visible_on_cache_hit(self):
        first = self.resolve()
        self.assertFalse(first.view.cache_hit)
        self.assertTrue(self.resolve().view.cache_hit)
        self.provider.failures = [ProviderFailure('throttled', retryable=True)]
        failed = self.resolve(refresh=True)
        hit = self.resolve()
        self.assertEqual((hit.error, hit.retry_at), (failed.error, failed.retry_at))
        self.clock.advance(2)
        self.assertIsNone(self.resolve().error)
        self.assertEqual(len(self.provider.calls), 3)

    def test_mixed_unavailable_response_is_not_complete(self):
        self.provider.responses[self.identity] = (
            replace(self.obs, observed_at='2026-10-04T10:59:00Z', fetched_at='2026-10-04T11:00:00Z'),
            replace(self.obs, observation_id='missing', observed_at='2026-10-04T10:59:00Z',
                    fetched_at='2026-10-04T11:00:00Z', unit_price=None))
        self.assertEqual(self.resolve().state, 'partial')
