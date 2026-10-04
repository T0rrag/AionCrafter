from dataclasses import replace
from decimal import localcontext
from fractions import Fraction
import unittest
from aioncrafter.codec import ValidationError
from aioncrafter.economics import SaleFees, amount, item_economics, materials_cost, units
from aioncrafter.models import CraftFee, FeeBasis, ItemQuantity, Money, Outcome, PriceType
from tests.helpers import catalog, market, observation


class EconomicsTests(unittest.TestCase):
    def setUp(self):
        self.c = catalog()
        self.m = market()
        self.r = self.c.recipes[0]
        self.r = replace(self.r, inputs=(ItemQuantity(self.c.items[0].identity, 1),),
                         outcomes=(Outcome((ItemQuantity(self.c.items[2].identity, 1),), '1', 'SYNTHETIC'),),
                         fees=(CraftFee(Money('500', self.m.currency), FeeBasis.BATCH),))
        self.target = ItemQuantity(self.c.items[2].identity, 1)
        self.obs = replace(observation(), unit_price='9300')
        self.fees = SaleFees('0.1', '0', 'floor', 'SYNTHETIC unverified assumption')

    def calc(self, **kwargs):
        args = dict(recipe=self.r, target=self.target, market=self.m, observations=(self.obs,),
                    selling_price='14500', sale_fees=self.fees)
        args.update(kwargs)
        return item_economics(**args)

    def test_brief_synthetic_regression(self):
        r = self.calc()
        self.assertEqual((r.craft_cost, r.proceeds, r.profit), (980000, 1305000, 325000))
        self.assertEqual(r.roi_percent, Fraction(325000 * 100, 980000))
        self.assertEqual(r.break_even, Fraction(9800000, 9))
        self.assertEqual(r.minimum_break_even_price, 1088889)

    def test_batches_leftovers_not_sold_and_fee_bases(self):
        recipe = replace(self.r, outcomes=(Outcome((ItemQuantity(self.target.item, 3),), '1', 'SYNTHETIC'),))
        r = self.calc(recipe=recipe, target=ItemQuantity(self.target.item, 4))
        self.assertEqual((r.crafts, r.produced, r.leftovers, r.planned_sales), (2, 6, 2, 4))
        for basis, expected in [(FeeBasis.ATTEMPT, 100000), (FeeBasis.BATCH, 100000), (FeeBasis.OUTPUT_UNIT, 300000)]:
            fee = CraftFee(Money('500', self.m.currency), basis)
            self.assertEqual(self.calc(recipe=recipe, target=ItemQuantity(self.target.item, 4), craft_fees=(fee,)).craft_cost, 1860000 + expected)

    def test_missing_never_zero_and_break_even_without_sale_price(self):
        r = self.calc(observations=())
        self.assertIsNone(r.craft_cost)
        self.assertIsNone(r.profit)
        self.assertEqual(r.materials.known_subtotal, 0)
        r = self.calc(selling_price=None)
        self.assertIsNotNone(r.break_even)
        self.assertIsNone(r.proceeds)
        self.assertIsNone(self.calc(recipe=replace(self.r, fees=None)).craft_cost)

    def test_zero_cost_and_full_tax(self):
        r = self.calc(observations=(replace(self.obs, unit_price='0'),), craft_fees=())
        self.assertEqual(r.craft_cost, 0)
        self.assertIsNone(r.roi_percent)
        self.assertIsNone(self.calc(sale_fees=SaleFees('1', '0', 'floor', 'SYNTHETIC')).break_even)

    def test_loss_fixed_fee_and_rounding_break_even_minimal(self):
        for rule in ('floor', 'ceil', 'half_up'):
            fees = SaleFees('0.333', '0.01', rule, 'SYNTHETIC')
            r = self.calc(sale_fees=fees, selling_price='1')
            self.assertLess(r.profit, 0)
            price = r.minimum_break_even_price
            self.assertGreaterEqual(self.calc(sale_fees=fees, selling_price=amount(price, self.m)).profit, 0)
            self.assertLess(self.calc(sale_fees=fees, selling_price=amount(price - 1, self.m)).profit, 0)

    def test_large_exact_values_ignore_decimal_context(self):
        value = '123456789012345678901234567890.12'
        with localcontext() as ctx:
            ctx.prec = 2
            self.assertEqual(amount(units(value, self.m), self.m), value)
            r = self.calc(observations=(replace(self.obs, unit_price=value),), craft_fees=())
            self.assertEqual(r.craft_cost, units(value, self.m))

    def test_merge_materials_and_reject_wrong_price_type_scope_duplicates(self):
        items = (ItemQuantity(self.obs.identity.item, 2), ItemQuantity(self.obs.identity.item, 3))
        self.assertEqual(materials_cost(items, self.m, (self.obs,)).total, 4650000)
        for obs in [(self.obs, self.obs), (replace(self.obs, price_type=PriceType.VENDOR_SELL_BACK),),
                    (replace(self.obs, identity=replace(self.obs.identity, market=replace(self.m, market_id='other'))),)]:
            with self.assertRaises(ValidationError):
                materials_cost(items, self.m, obs)

    def test_equivalent_deterministic_probability(self):
        recipe = replace(self.r, outcomes=(replace(self.r.outcomes[0], probability='1.0'),))
        self.assertEqual(self.calc(recipe=recipe).profit, 325000)

    def test_invalid_values_and_unknown_probabilities(self):
        for value in ('-1', '1.001', 'NaN'):
            with self.assertRaises(ValidationError):
                self.calc(selling_price=value)
        for value in ('-0.1', '1.1', 'NaN'):
            with self.assertRaises(ValidationError):
                SaleFees(value, '0', 'floor', 'SYNTHETIC')
        unknown = replace(self.r, outcomes=(replace(self.r.outcomes[0], probability=None),))
        with self.assertRaisesRegex(ValidationError, 'NONDETERMINISTIC'):
            self.calc(recipe=unknown)

    def test_joint_output_fees_charge_all_units_without_crediting_coproduct(self):
        outputs=(ItemQuantity(self.target.item,3),ItemQuantity(self.c.items[1].identity,2))
        recipe=replace(self.r,outcomes=(Outcome(outputs,'1','SYNTHETIC'),))
        for basis,expected in ((FeeBasis.ATTEMPT,200),(FeeBasis.BATCH,200),(FeeBasis.OUTPUT_UNIT,1000)):
            r=self.calc(recipe=recipe,target=ItemQuantity(self.target.item,4),
                        craft_fees=(CraftFee(Money('1',self.m.currency),basis),),
                        selling_price='10000',sale_fees=SaleFees('0','0','floor','SYNTHETIC'))
            self.assertEqual(r.crafting_fees,expected)
            self.assertEqual(r.profit,4000000-1860000-expected)
            self.assertEqual((r.produced,r.leftovers),(6,2))
            self.assertIn('coproducts_unvalued',r.issues)

    def test_multiple_fees_wrong_currency_and_fixed_fee_exceeding_proceeds(self):
        fees=(CraftFee(Money('1',self.m.currency),FeeBasis.BATCH),
              CraftFee(Money('2',self.m.currency),FeeBasis.OUTPUT_UNIT))
        self.assertEqual(self.calc(craft_fees=fees).crafting_fees,300)
        r=self.calc(selling_price='0',sale_fees=SaleFees('0','2','floor','SYNTHETIC'))
        self.assertEqual(r.proceeds,-200)
        self.assertEqual(r.profit,-980200)
        with self.assertRaisesRegex(ValidationError,'CURRENCY_MISMATCH'):
            self.calc(craft_fees=(CraftFee(Money('1',replace(self.m.currency,code='OTHER')),FeeBasis.BATCH),))
