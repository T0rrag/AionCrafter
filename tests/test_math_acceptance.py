"""Independent hand-calculated SYNTHETIC cases; derivations in PHASE_06_VALIDATION.md."""
from dataclasses import replace
from fractions import Fraction
import unittest

from aioncrafter.batches import plan_batches
from aioncrafter.buycraft import price_plan
from aioncrafter.codec import ValidationError
from aioncrafter.economics import SaleFees, item_economics
from aioncrafter.identity import PriceIdentity, Tradability
from aioncrafter.ledger import CraftRecord, Journal, OutputShare, RecordSource, SaleRecord, StockRecord, evaluate_journal
from aioncrafter.models import CraftFee, FeeBasis, ItemQuantity, Money, Outcome
from aioncrafter.plans import catalog_digest
from aioncrafter.stochastic import AttemptEvidence, BonusOutput, PlannedSale, attempt_economics
from aioncrafter.valuation import InventoryEntry
from tests.helpers import market, observation
from tests.synthetic_crafting import graph


class MathAcceptanceTests(unittest.TestCase):
    def test_hand_calculated_rounding_across_currency_scales(self):
        c, items = graph((('one', {'ore': 1}, {'end': 1}),))
        cases = (('floor', -1, -2, 4), ('ceil', 0, -1, 3), ('half_up', 0, -1, 3))
        for scale, minor in ((0, '1'), (2, '0.01'), (3, '0.001')):
            m = replace(market(), currency=replace(market().currency, decimal_places=scale))
            ref = replace(observation(), identity=PriceIdentity(items['ore'], m), unit_price=minor)
            for rounding, proceeds, profit, minimum in cases:
                with self.subTest(scale=scale, rounding=rounding):
                    result = item_economics(c.recipes[0], ItemQuantity(items['end'], 1), m, (ref,), minor,
                                            SaleFees('0.5', minor, rounding, 'SYNTHETIC'))
                    self.assertEqual(result.craft_cost, 1)
                    self.assertEqual((result.proceeds, result.profit), (proceeds, profit))
                    self.assertEqual(result.break_even, Fraction(4))
                    self.assertEqual(result.minimum_break_even_price, minimum)

    def shared_graph(self):
        c, i = graph((('shared', {'ore': 3}, {'bar': 4, 'dust': 1}),
                      ('left', {'bar': 2}, {'left': 1}), ('right', {'bar': 3}, {'right': 2}),
                      ('final', {'left': 1, 'right': 1}, {'final': 1})))
        fees = (('0.07', FeeBasis.OUTPUT_UNIT), ('0.11', FeeBasis.ATTEMPT),
                ('0.13', FeeBasis.BATCH), ('0.17', FeeBasis.BATCH))
        c = replace(c, recipes=tuple(replace(r, fees=(CraftFee(Money(value, market().currency), basis),))
                                     for r, (value, basis) in zip(c.recipes, fees)))
        refs = (replace(observation(), identity=PriceIdentity(i['ore'], market()), unit_price='1.23'),)
        return c, i, refs

    def test_shared_demand_joint_fees_stock_and_leftovers(self):
        c, i, refs = self.shared_graph()
        def plan(inventory=()):
            return plan_batches(c, (ItemQuantity(i['final'], 3),), tuple(r.recipe_id for r in c.recipes), inventory=inventory)
        replacement = plan()
        self.assertEqual({s.recipe.recipe_id: s.crafts for s in replacement.steps},
                         {'shared': 3, 'left': 3, 'right': 2, 'final': 3})
        self.assertEqual({q.item.item_id: q.quantity for q in replacement.leftovers}, {'dust': 3, 'right': 1})
        self.assertEqual(price_plan(replacement, market(), refs).crafting_fees, 215)
        self.assertEqual(price_plan(replacement, market(), refs).total, 1322)
        cash = plan((InventoryEntry(i['bar'], 1), InventoryEntry(i['ore'], 2)))
        self.assertEqual(cash.materials, (ItemQuantity(i['ore'], 7),))
        self.assertEqual({q.item.item_id: q.quantity for q in cash.inventory_remaining}, {'bar': 1, 'ore': 0})
        self.assertEqual(price_plan(cash, market(), refs).total, 1076)

    def test_missing_prices_zero_prices_and_unknown_fees_remain_distinct(self):
        c, i, refs = self.shared_graph()
        plan = plan_batches(c, (ItemQuantity(i['final'], 3),), tuple(r.recipe_id for r in c.recipes))
        missing = price_plan(plan, market(), ())
        self.assertEqual((missing.total, missing.known_materials, missing.known_fees), (None, 0, 215))
        self.assertEqual(price_plan(plan, market(), (replace(refs[0], unit_price='0'),)).total, 215)
        fees = price_plan(plan, market(), refs, fee_overrides={'shared': None})
        self.assertEqual((fees.total, fees.known_fees), (None, 110))

    def scenario(self, *, unknown=False, bonus=False):
        c, i = graph((('attempt', {'ore': 3}, {'normal': 2, 'dust': 1, 'rare': 1}),))
        m = market()
        q = lambda name, n: ItemQuantity(i[name], n)
        recipe = replace(c.recipes[0], outcomes=(
            Outcome((q('normal', 2), q('dust', 1)), '0.6', 'SYNTHETIC'),
            Outcome((q('normal', 1), q('rare', 1)), '0.25', 'SYNTHETIC'),
            Outcome((), None if unknown else '0.15', None if unknown else 'SYNTHETIC')),
            fees=(CraftFee(Money('0.02', m.currency), FeeBasis.ATTEMPT),
                  CraftFee(Money('0.01', m.currency), FeeBasis.OUTPUT_UNIT)))
        refs = (replace(observation(), identity=PriceIdentity(i['ore'], m), unit_price='0.07'),)
        sales = (PlannedSale(i['normal'], 1, Money('0.11', m.currency), SaleFees('0.5', '0.01', 'floor', 'SYNTHETIC')),
                 PlannedSale(i['rare'], 1, Money('1', m.currency), SaleFees('0.1', '0.03', 'half_up', 'SYNTHETIC')))
        bonuses = (BonusOutput('SYNTHETIC extra', (q('normal', 1),), '0.5', 'SYNTHETIC'),) if bonus else ()
        evidence = AttemptEvidence(recipe, bonuses, 'SYNTHETIC probabilities', 'SYNTHETIC full consumption', 'SYNTHETIC independent')
        return attempt_economics(recipe, m, refs, sales, evidence=evidence, bonuses=bonuses, max_scenarios=8)

    def test_joint_outcomes_failure_sale_caps_and_round_before_expectation(self):
        result = self.scenario()
        self.assertEqual([s.revenue for s in result.scenarios], [4, 91, 0])
        self.assertEqual([s.cost for s in result.scenarios], [26, 25, 23])
        self.assertEqual([s.profit for s in result.scenarios], [-22, 66, -23])
        self.assertEqual((result.expected_revenue, result.expected_cost, result.expected_profit),
                         (Fraction(503, 20), Fraction(253, 10), Fraction(-3, 20)))
        self.assertEqual((result.worst_profit, result.best_profit, result.loss_probability), (-23, 66, Fraction(3, 4)))

    def test_independent_bonus_can_reduce_profit_when_sale_is_capped(self):
        result = self.scenario(bonus=True)
        self.assertEqual([s.profit for s in result.scenarios], [-22, -23, 66, 65, -23, -20])
        self.assertEqual([s.probability for s in result.scenarios],
                         [Fraction(3, 10), Fraction(3, 10), Fraction(1, 8), Fraction(1, 8), Fraction(3, 40), Fraction(3, 40)])
        self.assertEqual((result.expected_revenue, result.expected_cost, result.expected_profit),
                         (Fraction(509, 20), Fraction(129, 5), Fraction(-7, 20)))

    def test_unknown_probability_and_bound_sale_fail_closed(self):
        self.assertIsNone(self.scenario(unknown=True).expected_profit)
        self.assertIsNone(self.scenario(unknown=True).loss_probability)
        _, i = graph((('one', {'ore': 1}, {'end': 1}),))
        bound = replace(i['end'], variant=replace(i['end'].variant, tradability=Tradability.BOUND))
        with self.assertRaisesRegex(ValidationError, 'TRADABILITY'):
            PlannedSale(bound, 1, Money('1', market().currency), SaleFees('0', '0', 'floor', 'SYNTHETIC'))

    def test_fifo_fractional_opening_purchase_joint_allocation_and_failure(self):
        c, i = graph((('craft', {'ore': 4}, {'bar': 3, 'dust': 2}),))
        m = market()
        q = lambda name, n: ItemQuantity(i[name], n)
        money = lambda value: Money(value, m.currency)
        source = lambda name: RecordSource(name, '2026-10-05T10:00:00Z', 'SYNTHETIC actual receipt')
        records = (
            StockRecord(source('opening'), 'opening', q('ore', 2), money('0.01')),
            StockRecord(source('purchase'), 'purchase', q('ore', 3), money('7.01')),
            CraftRecord(source('craft'), (q('ore', 4),), (q('bar', 3), q('dust', 2)), money('2'),
                        (OutputShare(i['bar'], '0.3'), OutputShare(i['dust'], '0.7'))),
            SaleRecord(source('sale'), q('bar', 2), money('10'), money('1')),
            CraftRecord(source('failure'), (q('dust', 1),), (), money('0.01'), None))
        result = evaluate_journal(Journal(1, 'SYNTHETIC acceptance', catalog_digest(c), m, 'fifo', records), c)
        self.assertEqual(result.realized_profit, Fraction(6377, 12))
        self.assertEqual(result.net_cash_flow, -2)
        self.assertEqual({b.item.item_id: (b.quantity, b.historical_basis) for b in result.inventory},
                         {'bar': (1, Fraction(401, 6)), 'dust': (1, Fraction(2807, 12)), 'ore': (1, Fraction(701, 3))})
