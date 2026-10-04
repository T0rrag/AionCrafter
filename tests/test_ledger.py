from dataclasses import replace
from fractions import Fraction
from pathlib import Path
import sqlite3
import tempfile
import unittest

from aioncrafter.codec import ValidationError
from aioncrafter.models import ItemQuantity, Money
from aioncrafter.plans import PlanStore, catalog_digest
from aioncrafter.ledger import (CraftRecord, Journal, LedgerStore, OutputShare, RecordSource, SaleRecord,
                               StockRecord, decode_journal, encode_journal, evaluate_journal)
from .helpers import market
from .synthetic_crafting import graph


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.c, self.i = graph((('craft', {'ore': 3}, {'bar': 2, 'dust': 1}),))
        self.m = market()
        self.journal = Journal(1, 'SYNTHETIC journal', catalog_digest(self.c), self.m, 'fifo', ())
        self.buy = StockRecord(self.source('buy'), 'purchase', self.q('ore', 3), self.money('10.00'))
        self.craft = CraftRecord(self.source('craft'), (self.q('ore', 3),), (self.q('bar', 2),), self.money('2.00'), None)
        self.sale = SaleRecord(self.source('sale'), self.q('bar', 1), self.money('10.00'), self.money('1.00'))

    def source(self, id):
        return RecordSource(id, '2026-10-04T10:00:00Z', 'SYNTHETIC user receipt')

    def money(self, amount):
        return Money(amount, self.m.currency)

    def q(self, name, quantity):
        return ItemQuantity(self.i[name], quantity)

    def journal_of(self, *records):
        return replace(self.journal, records=records)

    def test_recorded_profit_and_cash_differ_from_unsold_stock(self):
        result = evaluate_journal(self.journal_of(self.buy, self.craft, self.sale), self.c)
        self.assertEqual(result.realized_profit, 300)
        self.assertEqual(result.net_cash_flow, -300)
        self.assertEqual((result.inventory[0].quantity, result.inventory[0].historical_basis), (1, 600))
        # Full proceeds of unsold output are never inferred.
        self.assertEqual(result.realized_profit - result.net_cash_flow, result.inventory[0].historical_basis)

    def test_fractional_fifo_basis_preserves_exact_total(self):
        buy = replace(self.buy, total_paid=self.money('0.01'))
        sale = replace(self.sale, sold=self.q('ore', 1), gross_received=self.money('1'), fees_paid=self.money('0'))
        result = evaluate_journal(self.journal_of(buy, sale), self.c)
        self.assertEqual(result.realized_profit, Fraction(299, 3))
        self.assertEqual(result.inventory[0].historical_basis, Fraction(2, 3))
        sale2 = replace(sale, source=self.source('sale2'), sold=self.q('ore', 2))
        result = evaluate_journal(self.journal_of(buy, sale, sale2), self.c)
        self.assertEqual(result.realized_profit, 199)
        self.assertEqual(result.inventory, ())

    def test_fifo_consumes_oldest_lot_without_double_cost(self):
        buy2 = replace(self.buy, source=self.source('buy2'), total_paid=self.money('30'))
        sale = replace(self.sale, sold=self.q('ore', 4), gross_received=self.money('50'))
        result = evaluate_journal(self.journal_of(self.buy, buy2, sale), self.c)
        self.assertEqual(result.realized_profit, 2900)
        self.assertEqual(result.inventory[0].historical_basis, 2000)

    def test_opening_stock_cost_is_not_new_cash_outflow(self):
        opening = replace(self.buy, kind='opening')
        result = evaluate_journal(self.journal_of(opening, self.craft, self.sale), self.c)
        self.assertEqual(result.realized_profit, 300)
        self.assertEqual(result.net_cash_flow, 700)

    def test_unknown_opening_basis_does_not_become_free_material(self):
        opening = replace(self.buy, kind='opening', total_paid=None)
        result = evaluate_journal(self.journal_of(opening, self.craft, self.sale), self.c)
        self.assertIsNone(result.realized_profit)
        self.assertEqual(result.net_cash_flow, 700)
        self.assertIsNone(result.inventory[0].historical_basis)

    def test_multi_output_requires_explicit_allocation(self):
        craft = replace(self.craft, produced=(self.q('bar', 2), self.q('dust', 1)))
        result = evaluate_journal(self.journal_of(self.buy, craft, self.sale), self.c)
        self.assertIsNone(result.realized_profit)
        self.assertIn('multi_output_basis_unallocated', result.issues)
        craft = replace(craft, output_shares=(OutputShare(self.i['bar'], '0.75'), OutputShare(self.i['dust'], '0.25')))
        result = evaluate_journal(self.journal_of(self.buy, craft, self.sale), self.c)
        self.assertEqual(result.realized_profit, 450)
        self.assertEqual(sum(b.historical_basis for b in result.inventory), 750)

    def test_failed_craft_cost_is_expensed_and_no_output_is_promised(self):
        failure = replace(self.craft, produced=())
        result = evaluate_journal(self.journal_of(self.buy, failure), self.c)
        self.assertEqual((result.realized_profit, result.net_cash_flow, result.inventory), (-1200, -1200, ()))
        result = evaluate_journal(self.journal_of(self.buy, replace(failure, fee_paid=None)), self.c)
        self.assertIsNone(result.realized_profit)

    def test_missing_money_stays_unknown_but_explicit_zero_is_valid(self):
        result = evaluate_journal(self.journal_of(replace(self.buy, total_paid=None), self.craft, self.sale), self.c)
        self.assertIsNone(result.net_cash_flow)
        self.assertIsNone(result.realized_profit)
        result = evaluate_journal(self.journal_of(replace(self.buy, total_paid=self.money('0')), self.craft, self.sale), self.c)
        self.assertEqual(result.realized_profit, 800)
        result = evaluate_journal(self.journal_of(self.buy, self.craft, replace(self.sale, gross_received=None)), self.c)
        self.assertIsNone(result.realized_profit)
        self.assertIsNone(result.net_cash_flow)

    def test_duplicate_ids_overselling_order_and_scope_rejected(self):
        for records, code in (((self.buy, self.buy), 'DUPLICATE_ID'), ((self.sale,), 'INSUFFICIENT_STOCK'),
                              ((self.buy, replace(self.buy, source=self.source('opening'), kind='opening')), 'LEDGER_ORDER'),
                              ((self.buy, replace(self.craft, source=RecordSource('craft','2026-10-03T00:00:00Z','SYNTHETIC'))), 'LEDGER_ORDER')):
            with self.assertRaisesRegex(ValidationError, code):
                evaluate_journal(self.journal_of(*records), self.c)
        with self.assertRaisesRegex(ValidationError, 'LEDGER_CATALOG'):
            evaluate_journal(replace(self.journal, catalog_digest='other'), self.c)
        with self.assertRaisesRegex(ValidationError, 'CURRENCY_MISMATCH'):
            evaluate_journal(self.journal_of(replace(self.buy, total_paid=Money('1', replace(self.m.currency, code='OTHER')))), self.c)

    def test_invalid_allocation_not_normalized_or_guessed(self):
        with self.assertRaisesRegex(ValidationError, 'ALLOCATION'):
            replace(self.craft, output_shares=(OutputShare(self.i['bar'], '0.9'),))
        with self.assertRaisesRegex(ValidationError, 'ALLOCATION'):
            replace(self.craft, output_shares=(OutputShare(self.i['dust'], '1'),))

    def test_serialization_is_lossless_and_strict(self):
        journal = self.journal_of(self.buy, self.craft, self.sale)
        self.assertEqual(decode_journal(encode_journal(journal), self.c), journal)
        with self.assertRaises(ValidationError):
            decode_journal(b'{"schema_version":1}', self.c)
        with self.assertRaisesRegex(ValidationError, 'LEDGER_SIZE'):
            decode_journal(b' ' * (256*1024 + 1), self.c)

    def test_recorded_estimate_comparison_does_not_change_actual_profit(self):
        journal = replace(self.journal_of(self.buy, self.craft, self.sale), estimated_profit=self.money('5'))
        result = evaluate_journal(journal, self.c)
        self.assertEqual((result.realized_profit, result.recorded_estimate, result.realized_less_estimate), (300, 500, -200))
        self.assertEqual(decode_journal(encode_journal(journal), self.c), journal)
        missing = replace(journal, records=(replace(self.buy, total_paid=None), self.craft, self.sale))
        self.assertIsNone(evaluate_journal(missing, self.c).realized_less_estimate)

    def test_store_revisions_conflict_immutability_and_reopen(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / 'ledger.sqlite3')
            with LedgerStore(path) as store:
                self.assertEqual(store.save(self.journal_of(self.buy), self.c), 1)
                with self.assertRaisesRegex(ValidationError, 'CONCURRENT_CHANGE'):
                    store.save(self.journal_of(self.buy, self.craft), self.c, 0)
                with self.assertRaisesRegex(ValidationError, 'IMMUTABLE_RECORD'):
                    store.save(self.journal_of(replace(self.buy, total_paid=self.money('0'))), self.c, 1)
                self.assertEqual(store.save(self.journal_of(self.buy, self.craft), self.c, 1), 2)
            with LedgerStore(path) as store:
                revision, journal = store.load(self.journal.name, self.c)
                self.assertEqual((revision, journal.records), (2, (self.buy, self.craft)))

    def test_database_is_separate_and_failed_write_is_atomic(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / 'plans.sqlite3')
            with PlanStore(path):
                pass
            with self.assertRaisesRegex(ValidationError, 'LEDGER_DATABASE'):
                LedgerStore(path)
            with LedgerStore(str(Path(temp) / 'ledger.sqlite3')) as store:
                store.save(self.journal_of(self.buy), self.c)
                store.connection.execute("CREATE TRIGGER fail_save BEFORE INSERT ON journals BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
                with self.assertRaises(sqlite3.IntegrityError):
                    store.save(self.journal_of(self.buy, self.craft), self.c, 1)
                self.assertEqual(store.load(self.journal.name, self.c), (1, self.journal_of(self.buy)))

    def test_basis_conservation_over_sixty_synthetic_split_and_sale_cases(self):
        from random import Random
        rng = Random(404)
        for n in range(60):
            # Independently verify accounting conservation with non-divisible basis,
            # opening stock, added cash, joint outputs and partial completed sales.
            opening_cost = rng.randrange(1, 999)
            opening = replace(self.buy, kind='opening', acquired=self.q('ore', 2), total_paid=self.money(f'{opening_cost//100}.{opening_cost%100:02}'))
            buy = replace(self.buy, source=self.source('purchase'), total_paid=self.money('7.01'))
            craft = replace(self.craft, consumed=(self.q('ore', 4),), produced=(self.q('bar', 3), self.q('dust', 2)),
                            output_shares=(OutputShare(self.i['bar'], '0.3'), OutputShare(self.i['dust'], '0.7')))
            sale = replace(self.sale, sold=self.q('bar', rng.randrange(1, 4)))
            result = evaluate_journal(self.journal_of(opening, buy, craft, sale), self.c)
            with self.subTest(case=n):
                self.assertEqual(result.realized_profit - result.net_cash_flow,
                                 sum(b.historical_basis for b in result.inventory) - opening_cost)
