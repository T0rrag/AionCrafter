"""Synthetic recovery drills. Snapshots check SQLite structure, not game truth."""
from contextlib import closing
from dataclasses import replace
import hashlib
import http.client
import json
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from aioncrafter.catalog import import_catalog
from aioncrafter.codec import ValidationError, dumps
from aioncrafter.database import backup_database, check_database, export_catalog_release
from aioncrafter.ledger import Journal, LedgerStore, evaluate_journal
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

    def assert_web_starts(self, catalog_path, plans_path):
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        process = subprocess.Popen(
            [sys.executable, '-m', 'aioncrafter.web', '--catalog', str(catalog_path),
             '--plans', str(plans_path), '--port', str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            deadline = time.monotonic() + 8
            last_error = None
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    self.fail(f'web process exited early ({process.returncode})\nstdout={stdout}\nstderr={stderr}')
                connection = http.client.HTTPConnection('127.0.0.1', port, timeout=0.25)
                try:
                    connection.request('GET', '/')
                    response = connection.getresponse()
                    body = response.read()
                    if response.status == 200:
                        self.assertIn(b'AionCrafter', body)
                        return body
                    last_error = AssertionError(f'HTTP {response.status}')
                except (OSError, http.client.HTTPException) as exc:
                    last_error = exc
                    time.sleep(0.05)
                finally:
                    connection.close()
            self.fail(f'web process did not become ready: {last_error}')
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)

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

    def test_catalog_export_preserves_exact_json_and_refuses_overwrite(self):
        exported = self.root / 'catalog.json'
        with Store(self.source) as store:
            store.publish(self.c, expected_active=None)
        receipt = export_catalog_release(self.source, exported)
        self.assertEqual(receipt['release_id'], self.c.release_id)
        self.assertEqual(receipt['dataset_kind'], 'SYNTHETIC')
        self.assertEqual(exported.read_bytes(), dumps(self.c).encode())
        self.assertEqual(receipt['sha256'], hashlib.sha256(exported.read_bytes()).hexdigest())
        self.assertEqual(import_catalog(exported.read_bytes()), self.c)

        before = exported.read_bytes()
        with self.assertRaises(FileExistsError):
            export_catalog_release(self.source, exported, self.c.release_id)
        self.assertEqual(exported.read_bytes(), before)

        missing = self.root / 'missing-release.json'
        with self.assertRaisesRegex(ValidationError, 'CATALOG_NOT_FOUND'):
            export_catalog_release(self.source, missing, 'SYNTHETIC-does-not-exist')
        self.assertFalse(missing.exists())

    def test_catalog_export_rejects_bad_checksum_and_release_identity_without_output(self):
        bad_checksum = self.root / 'bad-checksum.sqlite3'
        with Store(bad_checksum) as store:
            store.publish(self.c, expected_active=None)
            store.connection.execute('UPDATE catalog_releases SET digest=? WHERE release_id=?',
                                     ('0' * 64, self.c.release_id))
        output = self.root / 'bad-checksum.json'
        with self.assertRaisesRegex(ValidationError, 'STORAGE_INTEGRITY'):
            export_catalog_release(bad_checksum, output, self.c.release_id)
        self.assertFalse(output.exists())

        bad_release = self.root / 'bad-release.sqlite3'
        mismatched = replace(self.c, release_id='SYNTHETIC-other-release')
        payload = dumps(mismatched)
        with Store(bad_release) as store:
            store.publish(self.c, expected_active=None)
            store.connection.execute('UPDATE catalog_releases SET payload=?, digest=? WHERE release_id=?',
                                     (payload, hashlib.sha256(payload.encode()).hexdigest(), self.c.release_id))
        output = self.root / 'bad-release.json'
        with self.assertRaisesRegex(ValidationError, 'STORAGE_INTEGRITY'):
            export_catalog_release(bad_release, output, self.c.release_id)
        self.assertFalse(output.exists())

    def test_recipe_change_launch_rejects_old_records_and_last_known_good_restore_recovers_them(self):
        catalog_db = self.root / 'catalog.sqlite3'
        plans_db = self.root / 'plans.sqlite3'
        ledger_db = Path(str(plans_db) + '.ledger.sqlite3')
        catalog_backup = self.root / 'catalog-before.sqlite3'
        plans_backup = self.root / 'plans-before.sqlite3'
        ledger_backup = self.root / 'ledger-before.sqlite3'
        original_json = self.root / 'catalog-before.json'
        changed_json = self.root / 'catalog-changed.json'

        plan = self.plan()
        journal = Journal(1, 'SYNTHETIC recovery', catalog_digest(self.c), market(), 'fifo', ())
        baseline_result = evaluate_journal(journal, self.c)
        with Store(catalog_db) as store:
            store.publish(self.c, expected_active=None)
            store.save_observation(observation(), release_id=self.c.release_id)
            store.save_calculation(calculation())
        with PlanStore(plans_db) as store:
            self.assertEqual(store.save(plan, self.c), 1)
            self.assertEqual(store.save(plan, self.c, 1), 2)
        with LedgerStore(ledger_db) as store:
            self.assertEqual(store.save(journal, self.c), 1)
            self.assertEqual(store.save(journal, self.c, 1), 2)

        export_catalog_release(catalog_db, original_json, self.c.release_id)
        backup_database(catalog_db, catalog_backup)
        backup_database(plans_db, plans_backup)
        backup_database(ledger_db, ledger_backup)

        changed_recipe = replace(
            self.c.recipes[0],
            requirements=(*self.c.recipes[0].requirements, 'SYNTHETIC: recipe-change recovery drill'),
        )
        changed = replace(
            self.c,
            release_id='SYNTHETIC-recipe-change-v2',
            recipes=(changed_recipe, *self.c.recipes[1:]),
        )
        with Store(catalog_db) as store:
            store.publish(changed, expected_active=self.c.release_id)
        export_catalog_release(catalog_db, changed_json)
        launched = import_catalog(changed_json.read_bytes())
        self.assertEqual(launched, changed)
        self.assert_web_starts(changed_json, plans_db)

        with closing(sqlite3.connect(plans_db)) as connection:
            plan_rows_before = connection.execute('SELECT * FROM plans ORDER BY name, revision').fetchall()
        with closing(sqlite3.connect(ledger_db)) as connection:
            journal_rows_before = connection.execute('SELECT * FROM journals ORDER BY name, revision').fetchall()
        with PlanStore(plans_db) as store:
            with self.assertRaisesRegex(ValidationError, 'PLAN_CATALOG'):
                store.load(plan.name, launched)
        with LedgerStore(ledger_db) as store:
            with self.assertRaisesRegex(ValidationError, 'LEDGER_CATALOG'):
                store.load(journal.name, launched)
        with closing(sqlite3.connect(plans_db)) as connection:
            self.assertEqual(connection.execute('SELECT * FROM plans ORDER BY name, revision').fetchall(), plan_rows_before)
        with closing(sqlite3.connect(ledger_db)) as connection:
            self.assertEqual(connection.execute('SELECT * FROM journals ORDER BY name, revision').fetchall(), journal_rows_before)

        restored_catalog_db = self.root / 'restored-catalog.sqlite3'
        restored_plans_db = self.root / 'restored-plans.sqlite3'
        restored_ledger_db = Path(str(restored_plans_db) + '.ledger.sqlite3')
        restored_json = self.root / 'restored-catalog.json'
        backup_database(catalog_backup, restored_catalog_db)
        backup_database(plans_backup, restored_plans_db)
        backup_database(ledger_backup, restored_ledger_db)
        export_catalog_release(restored_catalog_db, restored_json, self.c.release_id)
        restored_catalog = import_catalog(restored_json.read_bytes())
        self.assertEqual(restored_catalog, self.c)
        self.assertEqual(restored_json.read_bytes(), original_json.read_bytes())
        self.assert_web_starts(restored_json, restored_plans_db)

        with Store(restored_catalog_db) as store:
            self.assertEqual(store.active_release_id, self.c.release_id)
            self.assertEqual(store.observation('obs-1'), observation())
            self.assertEqual(store.calculation('calc-1'), calculation())
        with PlanStore(restored_plans_db) as store:
            self.assertEqual(store.load(plan.name, restored_catalog), (2, plan))
        with LedgerStore(restored_ledger_db) as store:
            revision, restored_journal = store.load(journal.name, restored_catalog)
            self.assertEqual(revision, 2)
            self.assertEqual(restored_journal, journal)
            self.assertEqual(evaluate_journal(restored_journal, restored_catalog), baseline_result)
        with Store(catalog_db) as store:
            self.assertEqual(store.active_release_id, changed.release_id)

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

    def test_offline_cli_backup_check_export_and_failure_exit_codes(self):
        with Store(self.source) as store:
            store.publish(self.c, expected_active=None)
        def run(*args):
            return subprocess.run([sys.executable, '-m', 'aioncrafter', *map(str, args)], capture_output=True, text=True)
        exported = self.root / 'catalog.json'
        result = run('export-catalog', '--database', self.source, '--output', exported)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['release_id'], self.c.release_id)
        self.assertEqual(import_catalog(exported.read_bytes()), self.c)
        result = run('export-catalog', '--database', self.source, '--output', exported)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)
        result = run('backup', '--database', self.source, '--output', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['kind'], 'catalog')
        result = run('check-database', '--database', self.backup)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = run('backup', '--database', self.source, '--output', self.backup)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)
