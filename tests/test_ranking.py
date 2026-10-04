from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction
import unittest

from aioncrafter.codec import ValidationError
from aioncrafter.economics import SaleFees
from aioncrafter.identity import PriceIdentity, Tradability
from aioncrafter.models import Acquisition, AcquisitionKind, ItemQuantity, Money, PriceType
from aioncrafter.ranking import CraftCandidate, RankingPolicy, RecipeAccess, rank_crafts
from aioncrafter.valuation import InventoryEntry
from .helpers import market, observation
from .synthetic_crafting import graph


class RankingTests(unittest.TestCase):
    def setUp(self):
        self.c, self.i = graph((('craft', {'ore': 2}, {'bar': 2}),))
        self.m = market()
        self.now = datetime(2026, 10, 4, 11, tzinfo=timezone.utc)
        self.ref = replace(observation(), identity=PriceIdentity(self.i['ore'], self.m),
                           observed_at='2026-10-04T10:00:00Z', unit_price='2.00')
        self.sale = replace(self.ref, observation_id='sale', identity=PriceIdentity(self.i['bar'], self.m), unit_price='10.00')
        self.fees = SaleFees('0.1', '1.00', 'floor', 'SYNTHETIC')
        self.candidate = CraftCandidate('SYNTHETIC-route', ItemQuantity(self.i['bar'], 1), ('craft',), self.sale, self.fees)
        self.policy = RankingPolicy(Money('20.00', self.m.currency), ('SYNTHETIC smith',),
                                    (RecipeAccess('craft', 'SYNTHETIC smith', 'SYNTHETIC source', ()),), (), 3600, 'profit')

    def rank(self, **kwargs):
        return rank_crafts(kwargs.pop('catalog', self.c), kwargs.pop('candidates', (self.candidate,)), self.m,
                           kwargs.pop('references', (self.ref,)), policy=kwargs.pop('policy', self.policy),
                           now=kwargs.pop('now', self.now), max_candidates=8, **kwargs)

    def test_exact_profit_roi_capital_and_conditional_warnings(self):
        row = self.rank().ranked[0]
        self.assertEqual((row.profit, row.capital_required, row.roi_percent), (400, 500, Fraction(100)))
        self.assertIn('stock_unverified', row.warnings)
        self.assertIn('sell_through_unknown', row.warnings)
        self.assertEqual(row.freshness, ('fresh', 'fresh'))

    def test_inventory_reduces_budget_cash_but_never_inflates_profit(self):
        policy = replace(self.policy, budget=Money('1.00', self.m.currency))
        row = self.rank(policy=policy, inventory=(InventoryEntry(self.i['ore'], 2),)).ranked[0]
        self.assertEqual((row.capital_required, row.profit), (100, 400))
        self.assertIn('over_budget', self.rank(policy=policy).excluded[0].excluded_reasons)

    def test_unknown_price_age_stale_and_future_are_excluded(self):
        for changed in (replace(self.ref, observed_at=None), replace(self.ref, observed_at='2026-10-04T09:59:59Z'),
                        replace(self.ref, fetched_at='2026-10-05T00:00:00Z')):
            result = self.rank(references=(changed,))
            self.assertEqual(result.ranked, ())
            self.assertIn('stale_future_or_unknown_price_age', result.excluded[0].excluded_reasons)

    def test_stale_selling_price_is_also_excluded(self):
        candidate = replace(self.candidate, selling_reference=replace(self.sale, observed_at=None))
        self.assertIn('stale_future_or_unknown_price_age', self.rank(candidates=(candidate,)).excluded[0].excluded_reasons)

    def test_incomplete_prices_or_fees_remain_visible_as_excluded(self):
        for refs in ((), (replace(self.ref, unit_price=None),)):
            row = self.rank(references=refs).excluded[0]
            self.assertIsNone(row.profit)
            self.assertIn('incomplete_prices_or_fees', row.excluded_reasons)
        for candidate in (replace(self.candidate, selling_reference=None), replace(self.candidate, sale_fees=None)):
            self.assertEqual(self.rank(candidates=(candidate,)).ranked, ())

    def test_profession_and_requirements_are_explicit_filters(self):
        self.assertIn('profession_filtered:craft', self.rank(policy=replace(self.policy, professions=())).excluded[0].excluded_reasons)
        self.assertIn('unknown_profession:craft', self.rank(policy=replace(self.policy, access=())).excluded[0].excluded_reasons)
        c = replace(self.c, recipes=(replace(self.c.recipes[0], requirements=('SYNTHETIC permit',)),))
        self.assertIn('unconfirmed_requirements:craft', self.rank(catalog=c).excluded[0].excluded_reasons)
        policy = replace(self.policy, access=(replace(self.policy.access[0], confirmed_requirements=('SYNTHETIC permit',)),))
        self.assertTrue(self.rank(catalog=c, policy=policy).ranked)
        c = replace(c, recipes=(replace(c.recipes[0], requirements=None),))
        self.assertIn('unknown_requirements:craft', self.rank(catalog=c, policy=policy).excluded[0].excluded_reasons)

    def test_joint_recipe_requirements_are_checked_for_intermediates(self):
        c, i = graph((('ingot', {'ore': 2}, {'ingot': 2}), ('end', {'ingot': 1}, {'bar': 1})))
        ref = replace(self.ref, identity=PriceIdentity(i['ore'], self.m))
        sale = replace(self.sale, identity=PriceIdentity(i['bar'], self.m))
        candidate = CraftCandidate('chain', ItemQuantity(i['bar'], 1), ('ingot', 'end'), sale, self.fees)
        policy = replace(self.policy, access=(RecipeAccess('end', 'SYNTHETIC smith', 'SYNTHETIC', ()),))
        row = self.rank(catalog=c, candidates=(candidate,), references=(ref,), policy=policy).excluded[0]
        self.assertIn('unknown_profession:ingot', row.excluded_reasons)

    def test_vendor_limit_currency_restrictions_and_reported_stock(self):
        vendor = replace(self.ref, price_type=PriceType.VENDOR_PURCHASE, available_quantity=2)
        acquisition = Acquisition(AcquisitionKind.VENDOR, self.m.currency, 2, ('SYNTHETIC permit',))
        c = replace(self.c, items=tuple(replace(item, acquisition=(acquisition,)) if item.identity == self.i['ore'] else item for item in self.c.items))
        row = self.rank(catalog=c, references=(vendor,)).excluded[0]
        self.assertIn('vendor_eligibility_unconfirmed:ore', row.excluded_reasons)
        policy = replace(self.policy, confirmed_vendor_restrictions=('SYNTHETIC permit',))
        self.assertTrue(self.rank(catalog=c, references=(vendor,), policy=policy).ranked)
        row = self.rank(catalog=c, references=(replace(vendor, available_quantity=1),), policy=policy).excluded[0]
        self.assertIn('insufficient_vendor_stock:ore', row.excluded_reasons)
        c = replace(c, items=tuple(replace(item, acquisition=(replace(acquisition, quantity_limit=1),)) if item.identity == self.i['ore'] else item for item in c.items))
        self.assertEqual(self.rank(catalog=c, references=(vendor,), policy=policy).ranked, ())

    def test_deterministic_ties_and_sort_objective(self):
        larger = replace(self.candidate, candidate_id='larger', target=ItemQuantity(self.i['bar'], 2))
        result = self.rank(candidates=(self.candidate, larger))
        self.assertEqual(result.ranked[0].candidate.candidate_id, 'larger')
        result = self.rank(candidates=(self.candidate, larger), policy=replace(self.policy, sort_by='capital'))
        self.assertEqual(result.ranked[0].candidate.candidate_id, 'SYNTHETIC-route')
        result = self.rank(candidates=(larger, self.candidate), policy=replace(self.policy, sort_by='roi'))
        self.assertEqual(result.ranked[0].candidate.candidate_id, 'larger')

    def test_zero_cost_roi_is_undefined_and_loss_not_ranked(self):
        result = self.rank(references=(replace(self.ref, unit_price='0'),), policy=replace(self.policy, sort_by='roi'))
        self.assertIn('undefined_roi', result.excluded[0].excluded_reasons)
        loss = replace(self.candidate, selling_reference=replace(self.sale, unit_price='0'))
        self.assertIn('nonpositive_profit', self.rank(candidates=(loss,)).excluded[0].excluded_reasons)

    def test_all_buy_is_not_presented_as_a_craft(self):
        row = self.rank(candidates=(replace(self.candidate, recipe_ids=()),), references=(self.ref, self.sale)).excluded[0]
        self.assertIn('no_crafting_required', row.excluded_reasons)

    def test_reported_thin_reference_cannot_pass_quantity_filter(self):
        row = self.rank(references=(replace(self.ref, available_quantity=1, price_type=PriceType.MINIMUM_LISTING),)).excluded[0]
        self.assertIn('insufficient_reported_quantity:ore', row.excluded_reasons)

    def test_bound_output_never_appears_as_market_opportunity(self):
        bound = replace(self.i['bar'], variant=replace(self.i['bar'].variant, tradability=Tradability.BOUND))
        c = replace(self.c, items=tuple(replace(item, identity=bound, acquisition=()) if item.identity == self.i['bar'] else item for item in self.c.items),
                    recipes=(replace(self.c.recipes[0], outcomes=(replace(self.c.recipes[0].outcomes[0], outputs=(ItemQuantity(bound, 2),)),)),))
        candidate = replace(self.candidate, target=ItemQuantity(bound, 1), selling_reference=None)
        row = self.rank(catalog=c, candidates=(candidate,)).excluded[0]
        self.assertIn('output_not_tradeable', row.excluded_reasons)

    def test_scope_sale_type_duplicates_and_policy_currency(self):
        with self.assertRaisesRegex(ValidationError, 'DUPLICATE_ID'):
            self.rank(candidates=(self.candidate, self.candidate))
        with self.assertRaisesRegex(ValidationError, 'SCOPE_MISMATCH'):
            self.rank(candidates=(replace(self.candidate, selling_reference=self.ref),))
        with self.assertRaisesRegex(ValidationError, 'PRICE_TYPE'):
            self.rank(candidates=(replace(self.candidate, selling_reference=replace(self.sale, price_type=PriceType.VENDOR_PURCHASE)),))
        with self.assertRaisesRegex(ValidationError, 'CURRENCY_MISMATCH'):
            self.rank(policy=replace(self.policy, budget=Money('20', replace(self.m.currency, code='OTHER'))))
