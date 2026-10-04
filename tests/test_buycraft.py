from dataclasses import replace
import unittest

from aioncrafter.acquisition import ListingOffer
from aioncrafter.batches import plan_batches
from aioncrafter.buycraft import ListingBook, compare_routes, price_plan
from aioncrafter.codec import ValidationError
from aioncrafter.identity import PriceIdentity
from aioncrafter.models import CraftFee, FeeBasis, ItemQuantity, Money, PriceType
from aioncrafter.valuation import InventoryEntry
from .helpers import market, observation
from .synthetic_crafting import graph
from .synthetic_prices import SyntheticProvider


class BuyCraftTests(unittest.TestCase):
    def setUp(self):
        self.c, self.i = graph((('ingot', {'ore': 3}, {'ingot': 2}), ('sword', {'ingot': 3}, {'sword': 1})))
        self.m = market()
        self.target = (ItemQuantity(self.i['sword'], 1),)
        self.refs = tuple(self.ref(name, price) for name, price in (('ore', '1.00'), ('ingot', '2.00'), ('sword', '9.00')))

    def ref(self, name, price):
        return replace(observation(), observation_id='SYNTHETIC-'+name, identity=PriceIdentity(self.i[name], self.m), unit_price=price)

    def compare(self, **kwargs):
        return compare_routes(self.c, self.target, ('ingot', 'sword'), self.m, self.refs,
                              objective=kwargs.pop('objective', 'additional_cash'), max_routes=4, **kwargs)

    def test_quantity_aware_intermediate_comparison(self):
        result = self.compare()
        # Crafting 3 ingots needs 2 batches/6 ore; it cannot use a fractional batch.
        totals = {r.selected_recipes: r.cost.total for r in result.routes}
        self.assertEqual(totals, {(): 900, ('ingot',): 900, ('sword',): 600, ('ingot', 'sword'): 600})
        self.assertEqual({r.cost.total for r in result.lowest_known}, {600})
        self.assertIn('stock_unverified', result.lowest_known[0].cost.issues)

    def test_all_executed_recipe_fees_and_joint_output_basis(self):
        c, i = graph((('joint', {'ore': 1}, {'a': 2, 'b': 3}), ('end', {'a': 3}, {'end': 1})))
        fee = CraftFee(Money('0.25', self.m.currency), FeeBasis.OUTPUT_UNIT)
        c = replace(c, recipes=(replace(c.recipes[0], fees=(fee,)),
                               replace(c.recipes[1], fees=(CraftFee(Money('1.00', self.m.currency), FeeBasis.BATCH),))))
        plan = plan_batches(c, (ItemQuantity(i['end'], 1),), ('joint', 'end'))
        ore = replace(observation(), identity=PriceIdentity(i['ore'], self.m), unit_price='2.00')
        cost = price_plan(plan, self.m, (ore,))
        self.assertEqual((cost.materials_total, cost.crafting_fees, cost.total), (400, 350, 750))

    def test_unknown_recipe_fee_keeps_total_unknown(self):
        self.c = replace(self.c, recipes=(replace(self.c.recipes[0], fees=None), self.c.recipes[1]))
        result = self.compare()
        route = next(r for r in result.routes if len(r.selected_recipes) == 2)
        self.assertIsNone(route.cost.total)
        self.assertEqual(result.unresolved_routes, 1)
        self.assertIn('unknown_crafting_fees:ingot', route.cost.issues)

    def test_explicit_fee_override_and_wrong_currency(self):
        fee = CraftFee(Money('2.00', self.m.currency), FeeBasis.ATTEMPT)
        result = self.compare(fee_overrides={'ingot': (fee,)})
        self.assertEqual(result.routes[-1].cost.total, 1000)
        bad = replace(fee, money=Money('2.00', replace(self.m.currency, code='OTHER')))
        with self.assertRaises(ValidationError):
            self.compare(fee_overrides={'ingot': (bad,)})

    def test_owned_stock_changes_cash_not_replacement_value(self):
        inv = (InventoryEntry(self.i['ingot'], 3),)
        cash = self.compare(inventory=inv)
        replacement = self.compare(inventory=inv, objective='replacement_cost')
        self.assertEqual(cash.lowest_known[0].cost.total, 0)
        self.assertEqual(replacement.lowest_known[0].cost.total, 600)

    def test_unknown_prices_are_not_zero_or_an_optimality_claim(self):
        self.refs = (self.ref('ore', '1.00'),)
        result = self.compare()
        self.assertEqual(result.unresolved_routes, 3)
        self.assertEqual(result.lowest_known[0].cost.total, 600)
        self.assertIn('all-or-nothing', result.scope)

    def test_no_known_cost_returns_no_lowest_route(self):
        self.refs = ()
        self.assertEqual(self.compare().lowest_known, ())

    def test_listing_stack_cost_and_insufficient_coverage(self):
        obs = replace(self.ref('ingot', None), price_type=PriceType.LISTING, available_quantity=4)
        book = ListingBook(obs.identity, (ListingOffer(obs, '10.00', False),), SyntheticProvider.capabilities)
        self.refs = tuple(r for r in self.refs if r.identity != obs.identity)
        result = self.compare(books=(book,))
        route = next(r for r in result.routes if r.selected_recipes == ('sword',))
        self.assertEqual(route.cost.total, 1000)
        self.assertEqual(route.cost.acquisitions[0].leftovers, 1)
        thin = ListingBook(obs.identity, (), SyntheticProvider.capabilities)
        route = next(r for r in self.compare(books=(thin,)).routes if r.selected_recipes == ('sword',))
        self.assertIsNone(route.cost.total)
        self.assertEqual(route.cost.acquisitions[0].missing, 3)

    def test_sale_history_does_not_price_acquisition(self):
        self.refs = tuple(replace(r, price_type=PriceType.COMPLETED_SALE) for r in self.refs)
        with self.assertRaisesRegex(ValidationError, 'PRICE_TYPE'):
            self.compare()

    def test_shared_demand_comparison_is_not_greedy_per_path(self):
        c, i = graph((('shared', {'ore': 1}, {'shared': 4}), ('a', {'shared': 2}, {'a': 1}),
                      ('b', {'shared': 2}, {'b': 1})))
        refs = tuple(replace(observation(), observation_id=name, identity=PriceIdentity(i[name], self.m), unit_price=p)
                     for name, p in (('ore', '3.00'), ('shared', '1.00'), ('a', '5.00'), ('b', '5.00')))
        result = compare_routes(c, (ItemQuantity(i['a'], 1), ItemQuantity(i['b'], 1)), ('shared', 'a', 'b'),
                                self.m, refs, objective='additional_cash', max_routes=8)
        self.assertEqual(result.lowest_known[0].cost.total, 300)

    def test_alternative_producers_are_compared_not_run_together(self):
        c, i = graph((('small', {'ore': 1}, {'a': 1}), ('big', {'ore': 2}, {'a': 3})))
        refs = (replace(observation(), identity=PriceIdentity(i['ore'], self.m), unit_price='1.00'),)
        result = compare_routes(c, (ItemQuantity(i['a'], 3),), ('small', 'big'), self.m, refs,
                                objective='replacement_cost', max_routes=4)
        self.assertEqual(len(result.routes), 3)
        self.assertEqual(result.lowest_known[0].selected_recipes, ('big',))

    def test_search_budget_and_duplicate_sources_fail_explicitly(self):
        with self.assertRaisesRegex(ValidationError, 'SEARCH_LIMIT'):
            compare_routes(self.c, self.target, ('ingot', 'sword'), self.m, self.refs,
                           objective='additional_cash', max_routes=3)
        self.refs = self.refs + self.refs[:1]
        with self.assertRaisesRegex(ValidationError, 'DUPLICATE_PRICE'):
            self.compare()

    def test_zero_cost_is_valid_and_unvalued_leftovers_are_visible(self):
        self.refs = tuple(replace(r, unit_price='0.00') for r in self.refs)
        result = self.compare()
        self.assertEqual(result.lowest_known[0].cost.total, 0)
        self.assertIn('leftovers_without_resale_credit', result.routes[-1].cost.issues)
