"""Transactional SQLite snapshots, immutable observations, and explicit rollback."""
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import sqlite3

from .catalog import validate_catalog
from .codec import dumps, loads, require
from .models import Calculation, Catalog, PriceObservation

SCHEMA_VERSION = 2
MIGRATIONS = {
    1: (
        "CREATE TABLE catalog_releases (release_id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL)",
        "CREATE TABLE active_catalog (singleton INTEGER PRIMARY KEY CHECK(singleton=1), release_id TEXT NOT NULL REFERENCES catalog_releases(release_id))",
    ),
    2: (
        "CREATE TABLE observations (observation_id TEXT PRIMARY KEY, release_id TEXT NOT NULL REFERENCES catalog_releases(release_id), price_key TEXT NOT NULL, supersedes_id TEXT REFERENCES observations(observation_id), payload TEXT NOT NULL)",
        "CREATE INDEX observations_price_key ON observations(price_key)",
        "CREATE TABLE calculations (calculation_id TEXT PRIMARY KEY, release_id TEXT NOT NULL REFERENCES catalog_releases(release_id), payload TEXT NOT NULL)",
    ),
}


@dataclass(frozen=True)
class CatalogDiff:
    added_items: tuple[str, ...]
    removed_items: tuple[str, ...]
    changed_items: tuple[str, ...]
    added_recipes: tuple[str, ...]
    removed_recipes: tuple[str, ...]
    changed_recipes: tuple[str, ...]


def compare_catalogs(before: Catalog | None, after: Catalog) -> CatalogDiff:
    def difference(old, new):
        return (tuple(sorted(new.keys() - old.keys())), tuple(sorted(old.keys() - new.keys())),
                tuple(sorted(k for k in new.keys() & old.keys() if new[k] != old[k])))
    old_items = {i.identity.key: i for i in before.items} if before else {}
    new_items = {i.identity.key: i for i in after.items}
    old_recipes = {r.recipe_id: r for r in before.recipes} if before else {}
    new_recipes = {r.recipe_id: r for r in after.recipes}
    return CatalogDiff(*difference(old_items, new_items), *difference(old_recipes, new_recipes))


class Store:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path, isolation_level=None)
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA busy_timeout=5000")
        try:
            self._migrate()
        except Exception:
            self.connection.close()
            raise

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @contextmanager
    def _transaction(self):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.connection.execute("COMMIT")
        except BaseException:
            self.connection.execute("ROLLBACK")
            raise

    def _migrate(self):
        with self._transaction():
            version = self.connection.execute("PRAGMA user_version").fetchone()[0]
            require(version <= SCHEMA_VERSION, "STORAGE_VERSION", "Database was created by a newer application")
            for target in range(version + 1, SCHEMA_VERSION + 1):
                for statement in MIGRATIONS[target]:
                    self.connection.execute(statement)
                self.connection.execute(f"PRAGMA user_version={target}")

    @property
    def active_release_id(self) -> str | None:
        row = self.connection.execute("SELECT release_id FROM active_catalog WHERE singleton=1").fetchone()
        return row[0] if row else None

    def catalog(self, release_id: str | None = None) -> Catalog:
        release_id = release_id if release_id is not None else self.active_release_id
        row = self.connection.execute("SELECT payload, digest FROM catalog_releases WHERE release_id=?", (release_id,)).fetchone()
        require(row is not None, "CATALOG_NOT_FOUND", str(release_id))
        require(hashlib.sha256(row[0].encode()).hexdigest() == row[1], "STORAGE_INTEGRITY", "Catalog checksum mismatch")
        result = loads(Catalog, row[0])
        validate_catalog(result)
        return result

    def _check_active(self, expected: str | None):
        require(self.active_release_id == expected, "CONCURRENT_CHANGE", "Active catalog changed; review the latest release before publishing")

    def publish(self, catalog: Catalog, *, expected_active: str | None) -> CatalogDiff:
        validate_catalog(catalog)
        payload = dumps(catalog)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        with self._transaction():
            self._check_active(expected_active)
            before = self.catalog(expected_active) if expected_active is not None else None
            diff = compare_catalogs(before, catalog)
            row = self.connection.execute("SELECT digest FROM catalog_releases WHERE release_id=?", (catalog.release_id,)).fetchone()
            require(row is None or row[0] == digest, "IMMUTABLE_RELEASE", "A release ID cannot be reused for changed content")
            if row is None:
                self.connection.execute("INSERT INTO catalog_releases VALUES (?,?,?)", (catalog.release_id, digest, payload))
            self.connection.execute("INSERT INTO active_catalog VALUES (1,?) ON CONFLICT(singleton) DO UPDATE SET release_id=excluded.release_id", (catalog.release_id,))
        return diff

    def rollback(self, release_id: str, *, expected_active: str) -> None:
        with self._transaction():
            self._check_active(expected_active)
            self.catalog(release_id)  # Verify the saved dataset before changing the pointer.
            self.connection.execute("UPDATE active_catalog SET release_id=? WHERE singleton=1", (release_id,))

    def save_observation(self, observation: PriceObservation, *, release_id: str) -> None:
        with self._transaction():
            catalog = self.catalog(release_id)
            require(observation.identity.item.key in {i.identity.key for i in catalog.items}, "ORPHAN_ITEM", "Observation item absent from its catalog release")
            if observation.supersedes_id is not None:
                original = self.observation(observation.supersedes_id)
                require(original.identity == observation.identity, "OVERRIDE", "Overrides must preserve exact price identity")
            existing = self.connection.execute("SELECT payload, release_id FROM observations WHERE observation_id=?", (observation.observation_id,)).fetchone()
            payload = dumps(observation)
            require(existing is None or existing == (payload, release_id), "IMMUTABLE_OBSERVATION", "Create a new observation ID to retain history")
            if existing is None:
                self.connection.execute("INSERT INTO observations VALUES (?,?,?,?,?)", (observation.observation_id, release_id, observation.identity.key, observation.supersedes_id, payload))

    def observation(self, observation_id: str) -> PriceObservation:
        row = self.connection.execute("SELECT payload FROM observations WHERE observation_id=?", (observation_id,)).fetchone()
        require(row is not None, "OBSERVATION_NOT_FOUND", observation_id)
        return loads(PriceObservation, row[0])

    def observations_for(self, identity) -> tuple[PriceObservation, ...]:
        rows = self.connection.execute("SELECT payload FROM observations WHERE price_key=? ORDER BY observation_id", (identity.key,)).fetchall()
        return tuple(loads(PriceObservation, r[0]) for r in rows)

    def save_calculation(self, calculation: Calculation) -> None:
        with self._transaction():
            catalog = self.catalog(calculation.catalog_release_id)
            item_keys = {i.identity.key for i in catalog.items}
            require(all(q.item.key in item_keys for q in calculation.inputs), "ORPHAN_ITEM", "Calculation item absent from catalog release")
            require(set(calculation.recipe_ids) <= {r.recipe_id for r in catalog.recipes}, "ORPHAN_RECIPE", "Calculation recipe absent from catalog release")
            for oid in calculation.observation_ids:
                obs = self.observation(oid)
                require(obs.identity.market == calculation.market, "SCOPE_MISMATCH", "Calculation references a different market/currency")
                require(obs.identity.item.key in item_keys, "ORPHAN_ITEM", "Observation item not in calculation catalog")
            payload = dumps(calculation)
            row = self.connection.execute("SELECT payload FROM calculations WHERE calculation_id=?", (calculation.calculation_id,)).fetchone()
            require(row is None or row[0] == payload, "IMMUTABLE_CALCULATION", "Save changed calculations under new IDs")
            if row is None:
                self.connection.execute("INSERT INTO calculations VALUES (?,?,?)", (calculation.calculation_id, calculation.catalog_release_id, payload))

    def calculation(self, calculation_id: str) -> Calculation:
        row = self.connection.execute("SELECT payload FROM calculations WHERE calculation_id=?", (calculation_id,)).fetchone()
        require(row is not None, "CALCULATION_NOT_FOUND", calculation_id)
        return loads(Calculation, row[0])
