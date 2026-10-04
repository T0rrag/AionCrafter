from dataclasses import replace
from pathlib import Path
import sqlite3
import tempfile
import unittest

from aioncrafter.codec import ValidationError, dumps
from aioncrafter.models import Alias, PriceType
from aioncrafter.storage import MIGRATIONS, Store
from tests.helpers import catalog, calculation, observation


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / "catalog.sqlite3")
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.c = catalog()
        self.store.publish(self.c, expected_active=None)

    def test_catalog_survives_reopen_and_migrations_are_idempotent(self):
        with Store(self.path) as second:
            self.assertEqual(second.catalog(), self.c)
            self.assertEqual(second.connection.execute("PRAGMA user_version").fetchone()[0], 2)

    def test_patch_diff_and_rollback_preserve_both_releases(self):
        item = replace(self.c.items[0], aliases=(*self.c.items[0].aliases, Alias("fr", "Minerai synthétique")))
        new = replace(self.c, release_id="SYNTHETIC-demo-v2", items=(item, *self.c.items[1:]))
        diff = self.store.publish(new, expected_active=self.c.release_id)
        self.assertEqual(diff.changed_items, (item.identity.key,))
        self.assertEqual(diff.removed_items, ())
        self.store.rollback(self.c.release_id, expected_active=new.release_id)
        self.assertEqual(self.store.catalog(), self.c)
        self.assertEqual(self.store.catalog(new.release_id), new)

    def test_invalid_import_does_not_change_last_known_good(self):
        bad = replace(self.c, release_id="invalid", items=self.c.items[1:])
        with self.assertRaises(ValidationError):
            self.store.publish(bad, expected_active=self.c.release_id)
        self.assertEqual(self.store.catalog(), self.c)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM catalog_releases").fetchone()[0], 1)

    def test_transaction_failure_rolls_back_insert_and_pointer(self):
        self.store.connection.execute("CREATE TRIGGER fail_activation BEFORE UPDATE ON active_catalog BEGIN SELECT RAISE(ABORT, 'simulated disk write failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.publish(replace(self.c, release_id="new"), expected_active=self.c.release_id)
        self.assertEqual(self.store.catalog(), self.c)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM catalog_releases").fetchone()[0], 1)

    def test_concurrent_stale_writer_cannot_overwrite_new_catalog(self):
        with Store(self.path) as second:
            self.store.publish(replace(self.c, release_id="new"), expected_active=self.c.release_id)
            with self.assertRaisesRegex(ValidationError, "CONCURRENT_CHANGE"):
                second.publish(replace(self.c, release_id="other"), expected_active=self.c.release_id)
        self.assertEqual(self.store.active_release_id, "new")

    def test_release_ids_are_immutable_but_exact_retries_work(self):
        self.store.publish(self.c, expected_active=self.c.release_id)
        with self.assertRaisesRegex(ValidationError, "IMMUTABLE_RELEASE"):
            self.store.publish(replace(self.c, recipes=()), expected_active=self.c.release_id)
        self.assertEqual(self.store.catalog(), self.c)

    def test_rollback_refuses_missing_corrupt_or_stale_release(self):
        with self.assertRaisesRegex(ValidationError, "CATALOG_NOT_FOUND"):
            self.store.rollback("missing", expected_active=self.c.release_id)
        with self.assertRaisesRegex(ValidationError, "CONCURRENT_CHANGE"):
            self.store.rollback(self.c.release_id, expected_active="stale")
        self.store.publish(replace(self.c, release_id="new"), expected_active=self.c.release_id)
        self.store.connection.execute("UPDATE catalog_releases SET payload='{}' WHERE release_id=?", (self.c.release_id,))
        with self.assertRaisesRegex(ValidationError, "STORAGE_INTEGRITY"):
            self.store.rollback(self.c.release_id, expected_active="new")
        self.assertEqual(self.store.active_release_id, "new")

    def test_observations_preserve_nulls_exact_amount_and_original_provenance(self):
        obs = observation()
        self.store.save_observation(obs, release_id=self.c.release_id)
        self.store.save_observation(obs, release_id=self.c.release_id)
        override = replace(obs, observation_id="override", supersedes_id=obs.observation_id,
                           unit_price="13.45", fetched_at="2026-10-04T12:00:00Z")
        self.store.save_observation(override, release_id=self.c.release_id)
        with Store(self.path) as second:
            self.assertEqual(second.observation(obs.observation_id), obs)
            self.assertEqual(second.observation("override"), override)
            self.assertEqual(len(second.observations_for(obs.identity)), 2)
            self.assertIsNone(second.observation(obs.observation_id).observed_at)

    def test_observation_mutation_or_cross_market_override_is_rejected(self):
        obs = observation()
        self.store.save_observation(obs, release_id=self.c.release_id)
        with self.assertRaisesRegex(ValidationError, "IMMUTABLE_OBSERVATION"):
            self.store.save_observation(replace(obs, unit_price="100"), release_id=self.c.release_id)
        wrong_market = replace(obs.identity, market=replace(obs.identity.market, market_id="other"))
        with self.assertRaisesRegex(ValidationError, "OVERRIDE"):
            self.store.save_observation(replace(obs, observation_id="override", supersedes_id="obs-1", identity=wrong_market), release_id=self.c.release_id)
        self.assertEqual(self.store.observations_for(wrong_market), ())

    def test_orphan_observation_is_rejected(self):
        obs = observation()
        unknown = replace(obs.identity, item=replace(obs.identity.item, item_id="missing"))
        with self.assertRaisesRegex(ValidationError, "ORPHAN_ITEM"):
            self.store.save_observation(replace(obs, identity=unknown), release_id=self.c.release_id)

    def test_calculation_record_roundtrip_without_running_engine(self):
        self.store.save_observation(observation(), release_id=self.c.release_id)
        calc = calculation()
        self.store.save_calculation(calc)
        with Store(self.path) as second:
            self.assertEqual(second.calculation(calc.calculation_id), calc)
        self.store.publish(replace(self.c, release_id="new"), expected_active=self.c.release_id)
        self.assertEqual(self.store.calculation(calc.calculation_id).catalog_release_id, self.c.release_id)
        with self.assertRaisesRegex(ValidationError, "IMMUTABLE_CALCULATION"):
            self.store.save_calculation(replace(calc, assumptions=("changed",)))

    def test_calculation_rejects_missing_observations_and_wrong_currency(self):
        calc = calculation()
        with self.assertRaisesRegex(ValidationError, "OBSERVATION_NOT_FOUND"):
            self.store.save_calculation(calc)
        obs = observation()
        currency = replace(obs.identity.market.currency, code="OTHER")
        obs = replace(obs, identity=replace(obs.identity, market=replace(obs.identity.market, currency=currency)))
        self.store.save_observation(obs, release_id=self.c.release_id)
        with self.assertRaisesRegex(ValidationError, "SCOPE_MISMATCH"):
            self.store.save_calculation(calc)


class MigrationTests(unittest.TestCase):
    def test_v1_to_v2_preserves_catalog(self):
        import hashlib
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "old.sqlite3")
            c = catalog()
            payload = dumps(c)
            with sqlite3.connect(path) as con:
                for statement in MIGRATIONS[1]:
                    con.execute(statement)
                con.execute("INSERT INTO catalog_releases VALUES (?,?,?)", (c.release_id, hashlib.sha256(payload.encode()).hexdigest(), payload))
                con.execute("INSERT INTO active_catalog VALUES (1,?)", (c.release_id,))
                con.execute("PRAGMA user_version=1")
            with Store(path) as store:
                self.assertEqual(store.catalog(), c)
                store.save_observation(observation(), release_id=c.release_id)
                self.assertEqual(store.observation("obs-1"), observation())

    def test_newer_schema_is_refused_without_downgrading(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "future.sqlite3")
            with sqlite3.connect(path) as con:
                con.execute("PRAGMA user_version=999")
            with self.assertRaisesRegex(ValidationError, "STORAGE_VERSION"):
                Store(path)
            with sqlite3.connect(path) as con:
                self.assertEqual(con.execute("PRAGMA user_version").fetchone()[0], 999)
