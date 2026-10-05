"""Synthetic recovery drills. Snapshots check SQLite structure, not game truth."""
from contextlib import closing
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from aioncrafter.codec import ValidationError, dumps
from aioncrafter.database import backup_database, check_database
from aioncrafter.ledger import Journal, LedgerStore
from aioncrafter.plans import PlanStore, SavedPlan, catalog_digest, encode_plan
from aioncrafter.storage import MIGRATIONS, Store
from aioncrafter.web import form_observations
from tests.helpers import catalog, calculation, market, observation


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / 'source.sqlite3'
        self.backup = self.root / 'backup.sqlite3'
        self.c = catalog()

    def plan(self):
        fields = dict(workflow='materials', market='test-server', market_kind='server',
                      faction_mode='not_applicable', currency='TEST', precision='2',
                      observed='2026-10-01T10:00:00Z', q0='3', p0='12.30')
        return SavedPlan(1, 'SYNTHETIC recovery', False, self.c.release_id, catalog_digest(self.c),
                         tuple(sorted(fields.items())), form_observations(self.c, fields),
                         '2026-10-05T10:00:00Z')

    def test_catalog_snapshot_preserves_history_and_rollback_on_restored_copy(self):
        with Store(self.source) as store:
            store.publish(self.c, expected_active=None)
            store.save_observation(observation(), release_id=self.c.release_id)
            store.save_calculation(calculation())
            store.publish(replace(self.c, release_id='SYNTHETIC-patch'), expected_active=self.c.release_id)
        receipt = backup_database(self.source, self.backup)
        self.assertEqual(receipt['kind'], 'catalog')
        self.assertEqual(receipt['sha256'], hashlib.sha256(self.backup.read_bytes()).hexdigest())
        restored = self.root / 'restored.sqlite3'
        backup_database(self.backup, restored)
        with Store(restored) as store:
            self.assertEqual(store.active_release_id, 'SYNTHETIC-patch')
            self.assertEqual(store.observation('obs-1'), observation())
            self.assertEqual(store.calculation('calc-1'), calculation())
            store.rollback(self.c.release_id, expected_active='SYNTHETIC-patch')
            self.assertEqual(store.catalog(), self.c)
        with Store(self.source) as store:
            self.assertEqual(store.active_release_id, 'SYNTHETIC-patch')

    def test_legacy_catalog_backup_is_readonly_and_only_restored_copy_migrates(self):
        payload = dumps(self.c)
        with closing(sqlite3.connect(self.source)) as connection, connection:
            for statement in MIGRATIONS[1]:
                connection.execute(statement)
            connection.execute('INSERT INTO catalog_releases VALUES (?,?,?)',
                               (self.c.release_id, hashlib.sha256(payload.encode()).hexdigest(), payload))
            connection.execute('INSERT INTO active_catalog VALUES (1,?)', (self.c.release_id,))
            connection.execute('PRAGMA user_version=1')
        before = self.source.read_bytes()
        self.assertEqual(check_database(self.source)['schema_version'], 1)
        backup_database(self.source, self.backup)
        self.assertEqual(self.source.read_bytes(), before)
        with Store(self.backup) as store:
            self.assertEqual(store.catalog(), self.c)
            self.assertEqual(store.connection.execute('PRAGMA user_version').fetchone()[0], 2)
        self.assertEqual(self.source.read_bytes(), before)

    def test_legacy_plan_backup_keeps_payload_and_migrates_only_copy(self):
        plan = self.plan()
        with closing(sqlite3.connect(self.source)) as connection, connection:
            connection.execute('CREATE TABLE plans (name TEXT, revision INTEGER, payload TEXT NOT NULL, PRIMARY KEY(name, revision))')
            connection.execute(f'PRAGMA application_id={PlanStore.APPLICATION_ID}')
            connection.execute('PRAGMA user_version=1')
            connection.execute('INSERT INTO plans VALUES (?,?,?)', (plan.name, 7, encode_plan(plan).decode()))
        before = self.source.read_bytes()
        backup_database(self.source, self.backup)
        with PlanStore(self.backup) as store:
            self.assertEqual(store.load(plan.name, self.c), (7, plan))
            self.assertEqual(store.save(plan, self.c, 7), 8)
        self.assertEqual(self.source.read_bytes(), before)

    def test_plan_tombstone_survives_restore_and_stale_tabs_still_fail(self):
        plan = self.plan()
        with PlanStore(self.source) as store:
            revision = store.save(plan, self.c)
            store.delete(plan.name, revision)
        backup_database(self.source, self.backup)
        with PlanStore(self.backup) as store:
            self.assertEqual(store.save(plan, self.c), 2)
            for operation in (lambda: store.save(plan, self.c, 1), lambda: store.delete(plan.name, 1)):
                with self.assertRaisesRegex(ValidationError, 'CONCURRENT_CHANGE'):
                    operation()

    def test_ledger_snapshot_preserves_all_immutable_revisions(self):
        journal = Journal(1, 'SYNTHETIC recovery', catalog_digest(self.c), market(), 'fifo', ())
        with LedgerStore(self.source) as store:
            store.save(journal, self.c)
            store.save(journal, self.c, 1)
            expected = store.connection.execute('SELECT * FROM journals ORDER BY revision').fetchall()
        backup_database(self.source, self.backup)
        with LedgerStore(self.backup) as store:
            self.assertEqual(store.connection.execute('SELECT * FROM journals ORDER BY revision').fetchall(), expected)
            self.assertEqual(store.load(journal.name, self.c), (2, journal))
            with self.assertRaisesRegex(ValidationError, 'CONCURRENT_CHANGE'):
                store.save(journal, self.c, 1)

    def test_backup_includes_committed_wal_data(self):
        with Store(self.source) as store:
            self.assertEqual(store.connection.execute('PRAGMA journal_mode=WAL').fetchone()[0], 'wal')
            store.publish(self.c, expected_active=None)
            self.assertTrue(Path(str(self.source) + '-wal').exists())
            backup_database(self.source, self.backup)
        with Store(self.backup) as restored:
            self.assertEqual(restored.catalog(), self.c)

    def test_existing_destination_and_same_source_are_never_overwritten(self):
        with Store(self.source) as store:
            store.publish(self.c, expected_active=None)
        self.backup.write_bytes(b'')
        before = self.source.read_bytes()
        for output in (self.backup, self.source):
            with self.assertRaises(FileExistsError):
                backup_database(self.source, output)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(self.backup.read_bytes(), b'')

    def test_orphaned_destination_sidecars_are_preserved(self):
        with Store(self.source) as store:
            store.publish(self.c, expected_active=None)
        for suffix in ('-wal', '-shm', '-journal'):
            with self.subTest(suffix=suffix):
                sidecar = Path(str(self.backup) + suffix)
                sidecar.write_bytes(b'preserve existing recovery data')
                with self.assertRaisesRegex(ValidationError, 'BACKUP_DESTINATION'):
                    backup_database(self.source, self.backup)
                self.assertEqual(sidecar.read_bytes(), b'preserve existing recovery data')
                self.assertFalse(self.backup.exists())
                sidecar.unlink()

    def test_missing_foreign_corrupt_and_future_sources_fail_without_output(self):
        with self.assertRaisesRegex(ValidationError, 'DATABASE_NOT_FOUND'):
            backup_database(self.source, self.backup)
        self.assertFalse(self.source.exists())
        self.source.write_bytes(b'not SQLite')
        with self.assertRaises(sqlite3.DatabaseError):
            backup_database(self.source, self.backup)
        self.source.unlink()
        with closing(sqlite3.connect(self.source)) as connection, connection:
            connection.execute('CREATE TABLE unrelated (id INTEGER)')
        before = self.source.read_bytes()
        with self.assertRaisesRegex(ValidationError, 'DATABASE_SCHEMA'):
            backup_database(self.source, self.backup)
        self.assertEqual(self.source.read_bytes(), before)
        self.source.unlink()
        with PlanStore(self.source) as store:
            store.connection.execute('PRAGMA user_version=999')
        before = self.source.read_bytes()
        with self.assertRaisesRegex(ValidationError, 'DATABASE_SCHEMA'):
            backup_database(self.source, self.backup)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertFalse(self.backup.exists())

    def test_failed_destination_validation_cleans_only_created_file(self):
        with Store(self.source) as store:
            store.publish(self.c, expected_active=None)
        before = self.source.read_bytes()
        with patch('aioncrafter.database.database_info', side_effect=[{}, ValidationError('DATABASE_INTEGRITY', 'injected')]):
            with self.assertRaises(ValidationError):
                backup_database(self.source, self.backup)
        self.assertFalse(self.backup.exists())
        self.assertEqual(self.source.read_bytes(), before)

    def test_sqlite_check_does_not_claim_payload_validation(self):
        with Store(self.source) as store:
            store.publish(self.c, expected_active=None)
            store.connection.execute("UPDATE catalog_releases SET payload='{}'")
        self.assertEqual(check_database(self.source)['payload_validation'], 'not_performed')
        backup_database(self.source, self.backup)
        with Store(self.backup) as store:
            with self.assertRaisesRegex(ValidationError, 'STORAGE_INTEGRITY'):
                store.catalog()

    def test_catalog_store_refuses_other_stores_and_foreign_schema_without_mutation(self):
        for factory in (PlanStore, LedgerStore):
            path = self.root / (factory.__name__ + '.sqlite3')
            with factory(path):
                pass
            before = path.read_bytes()
            with self.assertRaisesRegex(ValidationError, 'STORAGE_DATABASE'):
                Store(path)
            self.assertEqual(path.read_bytes(), before)
            with factory(path):
                pass
        with closing(sqlite3.connect(self.source)) as connection, connection:
            connection.execute('CREATE TABLE unrelated (id INTEGER)')
        before = self.source.read_bytes()
        with self.assertRaisesRegex(ValidationError, 'STORAGE_DATABASE'):
            Store(self.source)
        self.assertEqual(self.source.read_bytes(), before)

    def test_offline_cli_backup_check_and_failure_exit_codes(self):
        with Store(self.source) as store:
            store.publish(self.c, expected_active=None)
        def run(*args):
            return subprocess.run([sys.executable, '-m', 'aioncrafter', *map(str, args)], capture_output=True, text=True)
        result = run('backup', '--database', self.source, '--output', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['kind'], 'catalog')
        result = run('check-database', '--database', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = run('backup', '--database', self.source, '--output', self.backup)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)
