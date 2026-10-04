from dataclasses import replace
from decimal import Decimal, localcontext
import unittest

from aioncrafter.codec import ValidationError, dumps, loads
from aioncrafter.identity import Currency, Tradability
from aioncrafter.models import (AcquisitionKind, Completeness, CraftFee, FeeBasis, ItemQuantity,
                               Money, NamedAmount, Outcome, PriceObservation, PriceType)
from tests.helpers import catalog, calculation, market, observation


class ModelsTests(unittest.TestCase):
    def test_exact_money_roundtrip_and_loss_results(self):
        money = Money("123456789012345678901234567890.12", market().currency)
        self.assertEqual(loads(Money, dumps(money)).amount, money.amount)
        self.assertEqual(money.decimal, Decimal(money.amount))
        loss = NamedAmount("profit", Money("-12.34", market().currency))
        self.assertEqual(loads(NamedAmount, dumps(loss)), loss)

    def test_invalid_money_and_excess_precision(self):
        for value in [1, 1.1, True, "NaN", "Infinity", "1e2", "01", " 1", "1.001"]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                Money(value, market().currency)
        with self.assertRaises(ValidationError):
            CraftFee(Money("-0.01", market().currency), FeeBasis.ATTEMPT)
        with self.assertRaises(ValidationError):
            replace(observation(), unit_price="-1")

    def test_quantities_reject_bool_zero_negative_and_fraction(self):
        for value in [True, 0, -1, 0.5]:
            with self.assertRaises(ValidationError):
                ItemQuantity(catalog().items[0].identity, value)

    def test_joint_outputs_and_failure_are_representable(self):
        c = catalog()
        outputs = (ItemQuantity(c.items[2].identity, 2), ItemQuantity(c.items[1].identity, 1))
        recipe = replace(c.recipes[0], outcomes=(Outcome(outputs, "0.8", "SYNTHETIC"), Outcome((), "0.2", "SYNTHETIC")))
        self.assertEqual(recipe.outcomes[0].outputs[0].quantity, 2)
        self.assertEqual(recipe.outcomes[1].outputs, ())

    def test_probability_ranges_sum_and_provenance(self):
        recipe = catalog().recipes[0]
        for p in ["-0.1", "1.1", "NaN"]:
            with self.assertRaises(ValidationError):
                Outcome(recipe.outcomes[0].outputs, p, "SYNTHETIC")
        with self.assertRaises(ValidationError):
            Outcome(recipe.outcomes[0].outputs, "1", None)
        with self.assertRaises(ValidationError):
            replace(recipe, outcomes=(replace(recipe.outcomes[0], probability="0.9"),))
        with self.assertRaises(ValidationError):
            replace(recipe, outcomes=(recipe.outcomes[0], Outcome((), "0.1", "SYNTHETIC")))

    def test_probability_validation_does_not_round_with_decimal_context(self):
        recipe = catalog().recipes[0]
        with localcontext() as ctx:
            ctx.prec = 2
            good = (replace(recipe.outcomes[0], probability="0.999999999999999999999999999999"),
                    Outcome((), "0.000000000000000000000000000001", "SYNTHETIC"))
            self.assertEqual(len(replace(recipe, outcomes=good).outcomes), 2)
            with self.assertRaises(ValidationError):
                replace(recipe, outcomes=(good[0], replace(good[1], probability="0.000000000000000000000000000002")))

    def test_bound_cannot_have_auction_acquisition_or_listing(self):
        c = catalog()
        bound = c.items[-1]
        with self.assertRaises(ValidationError):
            replace(bound, acquisition=c.items[0].acquisition)
        obs = observation()
        with self.assertRaises(ValidationError):
            replace(obs, identity=replace(obs.identity, item=bound.identity), price_type=PriceType.LISTING)

    def test_sell_back_is_not_an_acquisition_price(self):
        self.assertFalse(replace(observation(), price_type=PriceType.VENDOR_SELL_BACK).acquisition_reference)
        self.assertFalse(replace(observation(), price_type=PriceType.COMPLETED_SALE).acquisition_reference)
        self.assertTrue(replace(observation(), price_type=PriceType.VENDOR_PURCHASE).acquisition_reference)

    def test_missing_price_stock_time_remain_null(self):
        obs = replace(observation(), unit_price=None)
        result = loads(PriceObservation, dumps(obs))
        self.assertIsNone(result.unit_price)
        self.assertIsNone(result.available_quantity)
        self.assertIsNone(result.observed_at)
        self.assertIsNotNone(result.fetched_at)

    def test_source_time_is_not_replaced_by_ingestion_time(self):
        obs = replace(observation(), observed_at="2026-10-03T22:00:00+02:00")
        newer_fetch = replace(obs, fetched_at="2026-10-04T12:00:00Z")
        self.assertEqual(obs.observed_at, newer_fetch.observed_at)
        for change in [{"observed_at": "2026-10-05T00:00:00Z"}, {"fetched_at": "2026-10-04T10:00:00"},
                       {"observed_at": "not a date"}]:
            with self.assertRaises(ValidationError):
                replace(obs, **change)

    def test_calculation_unknown_totals_and_currency(self):
        calc = calculation()
        with self.assertRaises(ValidationError):
            replace(calc, completeness=Completeness.COMPLETE)
        with self.assertRaisesRegex(ValidationError, "CURRENCY_MISMATCH"):
            replace(calc, results=(NamedAmount("total", Money("1", Currency("other", "TOKEN", 0))),))
        with self.assertRaises(ValidationError):
            replace(calc, inputs=())
