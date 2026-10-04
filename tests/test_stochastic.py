"""Fictional probabilities and evidence only; no game rules are established."""
from dataclasses import replace
from decimal import localcontext
from fractions import Fraction
import unittest

from aioncrafter.codec import ValidationError
from aioncrafter.economics import SaleFees
from aioncrafter.identity import PriceIdentity, Tradability
from aioncrafter.models import CraftFee, FeeBasis, ItemQuantity, Money, Outcome
from aioncrafter.stochastic import AttemptEvidence, BonusOutput, PlannedSale, attempt_economics
from .helpers import market, observation
from .synthetic_crafting import graph


class StochasticTests(unittest.TestCase):
    def setUp(self):
        self.c, self.i = graph((('attempt', {'ore': 2}, {'normal': 1, 'rare': 1}),))
        self.m = market()
        self.recipe = replace(self.c.recipes[0], outcomes=(
            Outcome((ItemQuantity(self.i['normal'], 1),), '0.5', 'SYNTHETIC success'),
            Outcome((ItemQuantity(self.i['rare'], 1),), '0.25', 'SYNTHETIC proc'),
            Outcome((), '0.25', 'SYNTHETIC failure')),
            fees=(CraftFee(Money('1.00', self.m.currency), FeeBasis.ATTEMPT),))
        self.refs = (replace(observation(), identity=PriceIdentity(self.i['ore'], self.m), unit_price='2.00'),)
        fees = SaleFees('0.1', '0.50', 'floor', 'SYNTHETIC assumed fees')
        self.sales = (PlannedSale(self.i['normal'], 1, Money('10.00', self.m.currency), fees),
                      PlannedSale(self.i['rare'], 1, Money('30.00', self.m.currency), fees))

    def evidence(self, bonuses=()):
        return AttemptEvidence(self.recipe, bonuses, 'SYNTHETIC probabilities',
                               'SYNTHETIC all inputs consumed even on failure', 'SYNTHETIC independent per attempt')

    def run_case(self, **kwargs):
        bonuses = kwargs.pop('bonuses', ())
        evidence = kwargs.pop('evidence', self.evidence(bonuses))
        return attempt_economics(self.recipe, self.m, kwargs.pop('references', self.refs),
                                 kwargs.pop('sales', self.sales), evidence=evidence, bonuses=bonuses,
                                 max_scenarios=kwargs.pop('max_scenarios', 64), **kwargs)

    def test_exclusive_outcomes_failure_and_exact_expectation(self):
        result = self.run_case()
        self.assertEqual([s.revenue for s in result.scenarios], [850, 2650, 0])
        self.assertEqual([s.cost for s in result.scenarios], [500, 500, 500])
        self.assertEqual(result.expected_profit, Fraction(1175, 2))
        self.assertEqual((result.worst_profit, result.best_profit, result.loss_probability), (-500, 2150, Fraction(1, 4)))
        self.assertEqual(result.expected_revenue - result.expected_cost, result.expected_profit)

    def test_unknown_probability_not_inferred_as_remainder(self):
        self.recipe = replace(self.recipe, outcomes=tuple(replace(o, probability=None, probability_source=None) if i == 2 else o
                                                        for i, o in enumerate(self.recipe.outcomes)))
        result = self.run_case()
        self.assertIsNone(result.expected_profit)
        self.assertIsNone(result.loss_probability)
        self.assertEqual(result.worst_profit, -500)

    def test_source_labels_alone_do_not_attest_probabilities(self):
        result = self.run_case(evidence=replace(self.evidence(), probabilities_ref=None))
        self.assertIsNone(result.expected_revenue)
        self.assertTrue(all(s.probability is None for s in result.scenarios))
        self.assertIn('unverified_probabilities', result.issues)

    def test_unknown_failure_consumption_keeps_cost_unknown(self):
        result = self.run_case(evidence=replace(self.evidence(), full_consumption_ref=None))
        self.assertIsNone(result.expected_cost)
        self.assertIsNone(result.worst_profit)
        self.assertIsNotNone(result.expected_revenue)

    def test_bonus_is_additive_not_alternative(self):
        bonus = BonusOutput('extra', (ItemQuantity(self.i['normal'], 2),), '0.5', 'SYNTHETIC bonus')
        sales = (replace(self.sales[0], quantity_limit=10), self.sales[1])
        result = self.run_case(bonuses=(bonus,), sales=sales)
        self.assertEqual(len(result.scenarios), 6)
        success_bonus = result.scenarios[1]
        self.assertEqual(success_bonus.outputs, (ItemQuantity(self.i['normal'], 3),))
        self.assertEqual(success_bonus.probability, Fraction(1, 4))
        self.assertEqual(sum(s.probability for s in result.scenarios), 1)
        # Independent bonus occurs even on failure under this explicit fictional rule.
        self.assertEqual(result.scenarios[-1].revenue, 1750)

    def test_unknown_bonus_independence_or_probability_keeps_expectation_unknown(self):
        bonus = BonusOutput('extra', (ItemQuantity(self.i['normal'], 1),), '0.5', 'SYNTHETIC')
        result = self.run_case(bonuses=(bonus,), evidence=replace(self.evidence((bonus,)), independent_bonuses_ref=None))
        self.assertIsNone(result.expected_profit)
        unknown = replace(bonus, probability=None, probability_source=None)
        self.assertIsNone(self.run_case(bonuses=(unknown,)).expected_profit)

    def test_output_fees_follow_actual_joint_outputs_and_bonus(self):
        self.recipe = replace(self.recipe, outcomes=(Outcome((ItemQuantity(self.i['normal'], 2), ItemQuantity(self.i['rare'], 3)),
                                                            '1', 'SYNTHETIC'),),
                              fees=(CraftFee(Money('0.25', self.m.currency), FeeBasis.OUTPUT_UNIT),))
        bonus = BonusOutput('extra', (ItemQuantity(self.i['normal'], 1),), '0.5', 'SYNTHETIC')
        result = self.run_case(bonuses=(bonus,))
        self.assertEqual([s.crafting_fees for s in result.scenarios], [125, 150])
        self.assertEqual(result.expected_cost, Fraction(1075, 2))
        self.assertEqual(sum(q.quantity for q in result.scenarios[1].leftovers), 4)

    def test_round_per_scenario_before_expected_value(self):
        sales = tuple(replace(s, unit_price=Money('0.01', self.m.currency),
                              fees=SaleFees('0.5', '0', 'half_up', 'SYNTHETIC')) for s in self.sales)
        with localcontext() as ctx:
            ctx.prec = 2
            result = self.run_case(sales=sales)
        self.assertEqual(result.expected_revenue, Fraction(3, 4))

    def test_unknown_prices_fees_and_no_sale_plan_do_not_silently_zero_costs(self):
        self.assertIsNone(self.run_case(references=()).expected_profit)
        self.assertIsNone(self.run_case(sales=(replace(self.sales[0], unit_price=None),)).expected_profit)
        self.assertIsNone(self.run_case(sales=(replace(self.sales[0], fees=None),)).expected_profit)
        result = self.run_case(sales=())
        self.assertEqual(result.expected_profit, -500)
        self.assertTrue(result.scenarios[0].leftovers)
        self.recipe = replace(self.recipe, fees=None)
        self.assertIsNone(self.run_case().expected_cost)

    def test_zero_probability_unknown_value_does_not_poison_expected_value(self):
        self.recipe = replace(self.recipe, outcomes=(replace(self.recipe.outcomes[0], probability='1'),
                                                     replace(self.recipe.outcomes[1], probability='0')))
        result = self.run_case(sales=(self.sales[0], replace(self.sales[1], unit_price=None)))
        self.assertEqual(result.expected_profit, 350)
        self.assertEqual((result.worst_profit, result.best_profit), (350, 350))

    def test_evidence_is_bound_to_exact_recipe_and_bonuses(self):
        old = self.evidence()
        self.recipe = replace(self.recipe, requirements=('SYNTHETIC different rule',))
        with self.assertRaisesRegex(ValidationError, 'EVIDENCE_SCOPE'):
            self.run_case(evidence=old)

    def test_invalid_sale_variant_currency_and_duplicate_are_rejected(self):
        bound = replace(self.i['normal'], variant=replace(self.i['normal'].variant, tradability=Tradability.BOUND))
        with self.assertRaisesRegex(ValidationError, 'TRADABILITY'):
            replace(self.sales[0], item=bound)
        with self.assertRaisesRegex(ValidationError, 'DUPLICATE_SALE'):
            self.run_case(sales=(self.sales[0], self.sales[0]))
        with self.assertRaisesRegex(ValidationError, 'CURRENCY_MISMATCH'):
            self.run_case(sales=(replace(self.sales[0], unit_price=Money('1', replace(self.m.currency, code='OTHER'))),))
        with self.assertRaisesRegex(ValidationError, 'OUTPUT'):
            self.run_case(sales=(replace(self.sales[0], item=self.i['ore']),))

    def test_bonus_scope_validation_and_bounded_work(self):
        bonus = BonusOutput('extra', (ItemQuantity(self.i['normal'], 1),), '0.5', 'SYNTHETIC')
        with self.assertRaisesRegex(ValidationError, 'SEARCH_LIMIT'):
            self.run_case(bonuses=(bonus,), max_scenarios=5)
        with self.assertRaisesRegex(ValidationError, 'BONUS'):
            self.run_case(bonuses=(bonus, bonus))
        foreign = replace(self.i['normal'], scope=replace(self.i['normal'].scope, build='other'))
        with self.assertRaisesRegex(ValidationError, 'SCOPE_MISMATCH'):
            self.run_case(bonuses=(replace(bonus, outputs=(ItemQuantity(foreign, 1),)),))

    def test_zero_sale_cap_needs_no_price_or_fee_and_credits_no_leftovers(self):
        result = self.run_case(sales=(replace(self.sales[0], quantity_limit=0, unit_price=None, fees=None),))
        self.assertEqual(result.expected_revenue, 0)
        self.assertEqual(result.loss_probability, 1)
        self.assertEqual(result.scenarios[0].sold, ())
