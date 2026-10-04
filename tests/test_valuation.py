from dataclasses import replace
import unittest

from aioncrafter.codec import ValidationError, dumps, loads
from aioncrafter.economics import materials_cost
from aioncrafter.identity import PriceIdentity
from aioncrafter.models import ItemQuantity, Money
from aioncrafter.valuation import HistoricalCost, InventoryEntry, value_materials
from tests.helpers import catalog, market, observation


class ValuationTests(unittest.TestCase):
    def setUp(self):
        self.c = catalog()
        self.m = market()
        self.item = self.c.items[0].identity
        self.obs = replace(observation(), unit_price='10')
        self.materials = materials_cost((ItemQuantity(self.item, 5),), self.m, (self.obs,))

    def record(self, quantity=5, cost='35'):
        return HistoricalCost(PriceIdentity(self.item, self.m), quantity, Money(cost, self.m.currency), 'SYNTHETIC purchase ledger row 1')

    def test_owned_materials_reduce_cash_not_replacement(self):
        result = value_materials(self.materials, self.m, (InventoryEntry(self.item, 3),))
        self.assertEqual(result.replacement_total, 5000)
        self.assertEqual(result.additional_cash, 2000)
        self.assertEqual((result.lines[0].owned_used, result.lines[0].to_buy), (3, 2))
        self.assertIsNone(result.recorded_total)

    def test_inventory_is_applied_once_to_merged_demand_and_capped(self):
        materials = materials_cost((ItemQuantity(self.item, 2), ItemQuantity(self.item, 3)), self.m, (self.obs,))
        self.assertEqual(value_materials(materials, self.m, (InventoryEntry(self.item, 3),)).additional_cash, 2000)
        self.assertEqual(value_materials(materials, self.m, (InventoryEntry(self.item, 9),)).lines[0].owned_used, 5)

    def test_full_inventory_missing_reference_cash_zero_replacement_unknown(self):
        materials = materials_cost((ItemQuantity(self.item, 5),), self.m, ())
        result = value_materials(materials, self.m, (InventoryEntry(self.item, 5),))
        self.assertEqual(result.additional_cash, 0)
        self.assertIsNone(result.replacement_total)
        self.assertIsNone(value_materials(materials, self.m).additional_cash)

    def test_complete_ledger_preserves_exact_recorded_value_and_explicit_zero(self):
        result = value_materials(self.materials, self.m, (), (self.record(),))
        self.assertEqual((result.replacement_total, result.additional_cash, result.recorded_total), (5000, 5000, 3500))
        self.assertEqual(value_materials(self.materials, self.m, (), (self.record(cost='0'),)).recorded_total, 0)
        self.assertEqual(loads(HistoricalCost, dumps(self.record())), self.record())

    def test_partial_and_overallocated_ledger_are_not_complete(self):
        result = value_materials(self.materials, self.m, (), (self.record(2, '14'),))
        self.assertIsNone(result.recorded_total)
        result = value_materials(self.materials, self.m, (), (self.record(2, '14'), self.record(3, '21')))
        self.assertEqual(result.recorded_total, 3500)
        with self.assertRaisesRegex(ValidationError, 'HISTORY_OVERALLOCATION'):
            value_materials(self.materials, self.m, (), (self.record(6),))

    def test_scope_variant_currency_and_invalid_quantities_are_not_coerced(self):
        for quantity in (True, -1, 1.5, '2'):
            with self.assertRaises(ValidationError):
                InventoryEntry(self.item, quantity)
        with self.assertRaisesRegex(ValidationError, 'DUPLICATE_INVENTORY'):
            value_materials(self.materials, self.m, (InventoryEntry(self.item, 1), InventoryEntry(self.item, 1)))
        other = replace(self.m, market_id='other')
        with self.assertRaisesRegex(ValidationError, 'SCOPE_MISMATCH'):
            value_materials(self.materials, self.m, (), (replace(self.record(), identity=PriceIdentity(self.item, other)),))
        with self.assertRaisesRegex(ValidationError, 'UNUSED_RECORD'):
            value_materials(self.materials, self.m, (), (replace(self.record(), identity=PriceIdentity(self.c.items[1].identity, self.m)),))
        with self.assertRaisesRegex(ValidationError, 'CURRENCY_MISMATCH'):
            replace(self.record(), total_cost=Money('1', replace(self.m.currency, code='OTHER')))
        for ref in ('', ' bad ', 'bad\nrecord'):
            with self.assertRaises(ValidationError):
                replace(self.record(), reference=ref)
