from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest

from aioncrafter.codec import ValidationError, dumps, loads
from aioncrafter.liquidity import SalesVolume, freshness, liquidity_evidence, quantity_label
from aioncrafter.models import PriceType
from .helpers import observation


class LiquidityTests(unittest.TestCase):
    def setUp(self):
        self.obs = replace(observation(), observed_at='2026-10-04T09:00:00Z', available_quantity=12)
        self.now = datetime(2026, 10, 4, 10, tzinfo=timezone.utc)
        self.age = timedelta(hours=1)
        self.volume = SalesVolume('SYNTHETIC-volume', self.obs.identity, 10, '2026-10-03T09:00:00Z',
                                  '2026-10-04T09:00:00Z', '2026-10-04T09:00:00Z',
                                  '2026-10-04T10:00:00Z', self.obs.provenance)

    def view(self, observations=(), volumes=()):
        return liquidity_evidence(self.obs.identity, observations, volumes, now=self.now, max_age=self.age)

    def test_asking_completed_and_reference_evidence_stay_separate(self):
        asking = replace(self.obs, price_type=PriceType.LISTING)
        sale = replace(self.obs, observation_id='sale', price_type=PriceType.COMPLETED_SALE)
        manual = replace(self.obs, observation_id='manual')
        result = self.view((asking, sale, manual))
        self.assertEqual(result.asking_prices, (asking,))
        self.assertEqual(result.completed_sales, (sale,))
        self.assertEqual(result.other_references, (manual,))
        self.assertIn('sales_volume_unknown', result.issues)
        self.assertIn('sell_through_unknown', result.issues)
        self.assertNotIn('12', quantity_label(sale))

    def test_zero_stock_is_distinct_from_unknown_stock(self):
        zero = replace(self.obs, price_type=PriceType.LISTING, available_quantity=0)
        unknown = replace(zero, available_quantity=None)
        self.assertIn('stock: 0', quantity_label(zero))
        self.assertIn('stock: unknown', quantity_label(unknown))
        self.assertNotIn('listing_stock_unknown', self.view((zero,)).issues)
        self.assertIn('listing_stock_unknown', self.view((unknown,)).issues)

    def test_volumes_are_not_summed_across_overlapping_sources(self):
        other = replace(self.volume, evidence_id='SYNTHETIC-overlap', sold_units=20)
        result = self.view(volumes=(self.volume, other))
        self.assertEqual(result.volumes, (self.volume, other))
        self.assertIn('sell_through_unknown', result.issues)
        self.assertNotIn('sales_volume_unknown', result.issues)
        self.assertEqual(loads(SalesVolume, dumps(self.volume)), self.volume)

    def test_zero_volume_is_evidence_and_unknown_volume_is_not_zero(self):
        self.assertNotIn('sales_volume_unknown', self.view(volumes=(replace(self.volume, sold_units=0),)).issues)
        self.assertIn('sales_volume_unknown', self.view(volumes=(replace(self.volume, sold_units=None),)).issues)

    def test_age_uses_source_time_and_inclusive_boundary(self):
        self.assertEqual(self.view((self.obs,)).freshness, ('fresh',))
        stale = replace(self.obs, observed_at='2026-10-04T08:59:59Z')
        self.assertEqual(self.view((stale,)).freshness, ('stale',))
        self.assertEqual(self.view((replace(stale, observed_at=None),)).freshness, ('unknown',))
        self.assertEqual(self.view((replace(stale, fetched_at='2026-10-05T00:00:00Z'),)).freshness, ('future',))

    def test_invalid_interval_clock_and_policy(self):
        for changes in ({'window_start':self.volume.window_end}, {'sold_units':-1},
                        {'observed_at':'2026-10-03T10:00:00Z'}, {'sold_units':True}):
            with self.assertRaises(ValidationError):
                replace(self.volume, **changes)
        with self.assertRaisesRegex(ValidationError, 'CLOCK'):
            freshness(None, self.obs.fetched_at, now=datetime(2026, 10, 4), max_age=self.age)
        with self.assertRaisesRegex(ValidationError, 'DURATION'):
            liquidity_evidence(self.obs.identity, (), (), now=self.now, max_age=-self.age)

    def test_scope_and_duplicate_evidence_rejected(self):
        with self.assertRaisesRegex(ValidationError, 'DUPLICATE_ID'):
            self.view((self.obs, self.obs))
        with self.assertRaisesRegex(ValidationError, 'DUPLICATE_ID'):
            self.view(volumes=(self.volume, self.volume))
        foreign = replace(self.volume, identity=replace(self.obs.identity, market=replace(self.obs.identity.market, market_id='other')))
        with self.assertRaisesRegex(ValidationError, 'SCOPE_MISMATCH'):
            self.view(volumes=(foreign,))

    def test_vendor_reference_does_not_establish_market_volume(self):
        vendor = replace(self.obs, price_type=PriceType.VENDOR_PURCHASE)
        self.assertIn('vendor stock: 12', quantity_label(vendor))
        self.assertIn('market sales volume unknown', quantity_label(vendor))
        self.assertIn('sales_volume_unknown', self.view((vendor,)).issues)
