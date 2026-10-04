from dataclasses import replace
from datetime import timedelta
import unittest

from aioncrafter.codec import ValidationError
from aioncrafter.price_cache import PriceCache
from .synthetic_prices import Clock, SyntheticProvider, sample


class PriceCacheTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.obs = sample()
        self.provider = SyntheticProvider((self.obs,))
        self.cache = PriceCache(self.provider, clock=self.clock, ttl=timedelta(seconds=30),
                                max_source_age=timedelta(hours=1))
        self.identity = self.obs.identity

    def test_hit_and_refresh_never_rejuvenate_source(self):
        first = self.cache.get(self.identity)
        self.assertEqual(first.freshness, ('fresh',))
        self.clock.advance(1)
        hit = self.cache.get(self.identity)
        self.assertTrue(hit.cache_hit)
        self.assertEqual(hit.freshness, ('stale',))
        self.clock.advance(29)
        refreshed = self.cache.get(self.identity)
        self.assertFalse(refreshed.cache_hit)
        self.assertEqual(refreshed.freshness, ('stale',))
        self.assertEqual(refreshed.entry.observations, (self.obs,))
        self.assertNotEqual(first.entry.retrieved_at, refreshed.entry.retrieved_at)
        self.assertEqual(len(self.provider.calls), 2)

    def test_unknown_zero_and_unavailable_are_distinct(self):
        unknown = replace(self.obs, observed_at=None, unit_price='0.00')
        unavailable = replace(unknown, observation_id='unavailable', unit_price=None)
        self.provider.responses[self.identity] = (unknown, unavailable)
        result = self.cache.get(self.identity)
        self.assertEqual(result.freshness, ('unknown', 'unknown'))
        self.assertEqual([o.unit_price for o in result.entry.observations], ['0.00', None])
        self.assertEqual(result.entry.observations[0].provenance, self.obs.provenance)

    def test_empty_response_is_cached_then_expires(self):
        self.provider.responses.clear()
        self.assertEqual(self.cache.get(self.identity).entry.observations, ())
        self.assertTrue(self.cache.get(self.identity).cache_hit)
        self.clock.advance(30)
        self.assertFalse(self.cache.get(self.identity).cache_hit)

    def test_wrong_scope_does_not_call_provider(self):
        other = replace(self.identity, market=replace(self.identity.market, market_id='elsewhere'))
        with self.assertRaises(ValidationError):
            self.cache.get(other)
        self.assertEqual(self.provider.calls, [])

    def test_variant_and_provider_caches_are_separate(self):
        other = replace(self.identity, item=replace(self.identity.item,
                        variant=replace(self.identity.item.variant, enhancement=9)))
        self.cache.get(self.identity)
        self.assertEqual(self.cache.get(other).entry.observations, ())
        separate = PriceCache(SyntheticProvider(), clock=self.clock, ttl=timedelta(seconds=30),
                              max_source_age=timedelta(hours=1))
        self.assertIsNone(separate.peek(self.identity))

    def test_invalid_refresh_preserves_last_good_and_rejects_mutated_id(self):
        self.cache.get(self.identity)
        self.provider.responses[self.identity] = (replace(self.obs, unit_price='99.00'),)
        with self.assertRaises(ValidationError):
            self.cache.get(self.identity, refresh=True)
        self.assertEqual(self.cache.peek(self.identity).entry.observations, (self.obs,))

    def test_batch_validation_is_atomic(self):
        other = replace(self.identity, item=replace(self.identity.item, item_id='other'))
        with self.assertRaises(ValidationError):
            self.cache.store_batch({self.identity: (self.obs,), other: (self.obs,)})
        self.assertIsNone(self.cache.peek(self.identity))

    def test_clock_rollback_flags_future_and_expired(self):
        self.cache.get(self.identity)
        self.clock.advance(-3601)
        view = self.cache.peek(self.identity)
        self.assertEqual(view.freshness, ('future',))
        self.assertTrue(view.cache_expired)

    def test_timezone_equivalence_and_future_ingestion(self):
        equivalent = replace(self.obs, observed_at='2026-10-04T12:00:00+02:00')
        self.provider.responses[self.identity] = (equivalent,)
        self.assertEqual(self.cache.get(self.identity).freshness, ('fresh',))
        self.provider.responses[self.identity] = (replace(self.obs, observation_id='future',
                                                        fetched_at='2026-10-04T11:00:00.001Z'),)
        with self.assertRaises(ValidationError):
            self.cache.get(self.identity, refresh=True)

    def test_invalid_policy_and_naive_clock(self):
        with self.assertRaises(ValidationError):
            PriceCache(self.provider, clock=self.clock, ttl=timedelta(seconds=-1),
                       max_source_age=timedelta(0))
        self.clock.now = self.clock.now.replace(tzinfo=None)
        with self.assertRaises(ValidationError):
            self.cache.get(self.identity)

    def test_duplicate_records_and_capability_changes_rejected(self):
        self.provider.responses[self.identity] = (self.obs, self.obs)
        with self.assertRaises(ValidationError):
            self.cache.get(self.identity)
        self.provider.capabilities = replace(self.provider.capabilities, source_timestamps=False)
        with self.assertRaises(ValidationError):
            self.cache.get(self.identity)

    def test_remembered_observation_validation_is_atomic(self):
        other = replace(self.obs, observation_id='invalid', fetched_at='2026-10-04T12:00:00Z')
        with self.assertRaises(ValidationError):
            self.cache.remember_observations((self.obs, other))
        # A rejected batch did not pin the earlier, otherwise-valid record.
        corrected = replace(self.obs, unit_price='1.00')
        self.cache.remember_observations((corrected,))
        self.assertIsNone(self.cache.peek(self.identity))
        with self.assertRaisesRegex(ValidationError, 'IMMUTABLE_ID'):
            self.cache.store_batch({self.identity: (self.obs,)})

    def test_invalid_response_mapping_is_rejected(self):
        with self.assertRaisesRegex(ValidationError, 'TYPE'):
            self.cache.store_batch([(self.identity, (self.obs,))])
