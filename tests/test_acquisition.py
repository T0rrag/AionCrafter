from dataclasses import replace
from decimal import localcontext
from itertools import product
import random
import unittest

from aioncrafter.acquisition import ListingOffer, depth_cost, indicative_cost
from aioncrafter.codec import ValidationError
from aioncrafter.models import PriceType
from .synthetic_prices import SyntheticProvider, sample


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.obs = sample(price_type=PriceType.LISTING)
        self.identity = self.obs.identity
        self.capabilities = SyntheticProvider.capabilities

    def offer(self, name, qty, total, partial=False, unit=None):
        return ListingOffer(replace(self.obs, observation_id=name, available_quantity=qty, unit_price=unit), total, partial)

    def cost(self, qty, *offers, **kwargs):
        return depth_cost(self.identity, qty, offers, self.capabilities, max_states=kwargs.get('max_states', 10000))

    def test_divisible_depth_consumes_multiple_price_levels(self):
        result = self.cost(5, self.offer('a', 3, '3.00', True, '1.00'), self.offer('b', 4, '8.00', True, '2.00'))
        self.assertEqual((result.total, result.purchased, result.missing), (700, 5, 0))
        self.assertEqual([p.quantity for p in result.purchases], [3, 2])
        self.assertEqual(result.stock, 'snapshot_only')

    def test_whole_stack_optimizes_total_cash_not_unit_price(self):
        # Cheapest per unit is the big stack, but buying it costs more.
        result = self.cost(6, self.offer('big', 10, '10.00'), self.offer('small', 6, '7.20'))
        self.assertEqual(result.total, 720)
        self.assertEqual(result.purchases[0].observation_id, 'small')

    def test_whole_stack_overbuy_and_indivisible_price(self):
        result = self.cost(2, self.offer('stack', 3, '1.00'))
        self.assertEqual((result.total, result.purchased, result.leftovers), (100, 3, 1))

    def test_mixed_whole_and_divisible_is_exact(self):
        result = self.cost(7, self.offer('stack', 5, '3.00'), self.offer('units', 9, '9.00', True, '1.00'))
        self.assertEqual(result.total, 500)
        self.assertEqual(result.purchased, 7)

    def test_insufficient_stock_exposes_subtotal_and_no_full_total(self):
        result = self.cost(5, self.offer('only', 2, '3.00'))
        self.assertEqual((result.state, result.known_cost, result.total, result.missing), ('insufficient', 300, None, 3))
        empty = self.cost(5)
        self.assertEqual((empty.known_cost, empty.total, empty.missing), (0, None, 5))

    def test_known_zero_is_valid_covered_cost(self):
        result = self.cost(3, self.offer('free', 4, '0.00'))
        self.assertEqual((result.state, result.total, result.leftovers), ('covered', 0, 1))

    def test_reference_and_minimum_only_are_indicative_stock_unverified(self):
        for kind in (PriceType.MINIMUM_LISTING, PriceType.SNAPSHOT, PriceType.MANUAL):
            result = indicative_cost(self.identity, 100, replace(self.obs, price_type=kind, available_quantity=1))
            self.assertEqual((result.state, result.stock, result.total), ('indicative', 'unverified', 123000))
            self.assertEqual(result.purchased, 0)
        self.assertIsNone(indicative_cost(self.identity, 1, None).total)
        self.assertIsNone(indicative_cost(self.identity, 1, replace(self.obs, unit_price=None)).total)

    def test_completed_sales_and_sellback_do_not_price_acquisition(self):
        for kind in (PriceType.COMPLETED_SALE, PriceType.VENDOR_SELL_BACK):
            with self.assertRaises(ValidationError):
                indicative_cost(self.identity, 2, replace(self.obs, price_type=kind))
            with self.assertRaises(ValidationError):
                ListingOffer(replace(self.obs, price_type=kind, available_quantity=2), '24.60', False)

    def test_scope_duplicate_snapshot_and_capabilities_validation(self):
        offer = self.offer('a', 2, '3.00')
        other = replace(offer, observation=replace(offer.observation, identity=replace(self.identity,
                        market=replace(self.identity.market, market_id='other'))))
        later = replace(offer, observation=replace(offer.observation, observation_id='later', fetched_at='2026-10-04T10:01:00Z'))
        for offers in ((offer, offer), (other,), (offer, later)):
            with self.assertRaises(ValidationError):
                self.cost(1, *offers)
        with self.assertRaises(ValidationError):
            depth_cost(self.identity, 1, (offer,), replace(self.capabilities, listing_depth=False), max_states=100)

    def test_offer_semantics_cannot_be_guessed(self):
        for args in [('a', 0, '0.00', False, None), ('a', 3, '1.00', True, None),
                     ('a', 2, '1.00', False, '1.00')]:
            with self.assertRaises(ValidationError):
                self.offer(*args)
        with self.assertRaises(ValidationError):
            self.cost(True)

    def test_huge_amounts_do_not_depend_on_decimal_context(self):
        with localcontext() as context:
            context.prec = 3
            total = '123456789012345678901234567890.12'
            result = self.cost(1, self.offer('huge', 1, total))
            self.assertEqual(result.total, 12345678901234567890123456789012)

    def test_search_limit_fails_without_claiming_an_optimum(self):
        with self.assertRaisesRegex(ValidationError, 'SEARCH_LIMIT'):
            self.cost(4, self.offer('a', 2, '1.00'), self.offer('b', 3, '2.00'), max_states=1)

    def test_deterministic_small_books_match_exhaustive_oracle(self):
        rng = random.Random(303)
        for case in range(60):
            offers = []
            specs = []
            for i in range(4):
                qty, cents, partial = rng.randint(1, 5), rng.randint(0, 9), bool(rng.getrandbits(1))
                total = qty * cents
                offers.append(self.offer(str(i), qty, f'{total // 100}.{total % 100:02}', partial, f'0.{cents:02}'))
                specs.append((qty, cents, partial))
            demand = rng.randint(1, sum(q for q, _, _ in specs))
            possibilities = []
            for counts in product(*(range(q + 1) if partial else (0, q) for q, _, partial in specs)):
                if sum(counts) >= demand:
                    possibilities.append((sum(n*p for n, (_, p, _) in zip(counts, specs)), sum(counts)))
            expected = min(possibilities)
            actual = self.cost(demand, *offers)
            with self.subTest(case=case):
                self.assertEqual((actual.total, actual.purchased), expected)
