"""Versioned local plans and lossless JSON/CSV transfer. No external services."""
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import io
import json
import re
import sqlite3

from .codec import dumps, loads, require, validate_fields
from .identity import identifier
from .models import Catalog, PriceObservation, timestamp

MAX_PLAN_BYTES = 256 * 1024


@dataclass(frozen=True)
class SavedPlan:
    schema_version: int
    name: str
    favorite: bool
    catalog_release_id: str
    catalog_digest: str
    fields: tuple[tuple[str, str], ...]
    observations: tuple[PriceObservation, ...]
    saved_at: str

    def __post_init__(self):
        validate_fields(self)
        require(self.schema_version == 1, 'PLAN_VERSION', 'Supported plan schema is 1')
        identifier(self.name, 'plan name')
        identifier(self.catalog_release_id, 'catalog release')
        require(re.fullmatch('[a-f0-9]{64}', self.catalog_digest) is not None, 'PLAN_CATALOG', 'Invalid catalog digest')
        require(len(dict(self.fields)) == len(self.fields), 'DUPLICATE_FIELD', 'Plan form fields repeat')
        require(len(self.fields) <= 200 and all(len(v) <= 65536 for _, v in self.fields), 'PLAN_SIZE', 'Plan fields exceed limits')
        timestamp(self.saved_at)


def catalog_digest(catalog: Catalog) -> str:
    return hashlib.sha256(dumps(catalog).encode()).hexdigest()


def validate_plan(plan: SavedPlan, catalog: Catalog) -> None:
    require(plan.catalog_release_id == catalog.release_id and plan.catalog_digest == catalog_digest(catalog),
            'PLAN_CATALOG', 'Plan belongs to a different catalog release or content; explicit migration required')
    fixed = {'workflow','market','market_kind','faction_mode','faction','currency','precision','observed',
             'paste','language','product','recipe','target','selling','craft_fee','craft_basis','tax',
             'sale_fee','rounding','fee_source','product_search','plan_mode','plan_objective'}
    indexed = {f'{prefix}{i}' for i in range(len(catalog.items)) for prefix in ('p','t','q','owned','hqty','hcost','href')}
    indexed.update(f'use_recipe{i}' for i in range(len(catalog.recipes)))
    require(all(k in fixed or k in indexed or re.fullmatch('pick[0-9]{1,3}', k) for k, _ in plan.fields),
            'PLAN_FIELD', 'Plan contains an unsupported field')
    require(dict(plan.fields).get('workflow') in ('materials', 'item', 'crafting'), 'PLAN_INPUT', 'Select a workflow')
    from .references import validate_references
    if plan.observations:
        validate_references(plan.observations, catalog, plan.observations[0].identity.market)
    require(len({o.observation_id for o in plan.observations}) == len(plan.observations), 'PLAN_OBSERVATIONS', 'Observation IDs repeat')
    # Use the same input checks as calculation, without storage/network side effects.
    from .web import render
    result = render(catalog, dict(plan.fields), supplied_observations=plan.observations)
    require('role="alert"' not in result, 'PLAN_INPUT', 'Plan inputs do not form a valid calculation; calculate before saving')
    require(len(plan.observations) == len(catalog.items), 'PLAN_OBSERVATIONS', 'Plan needs one explicit observation state per item')


def encode_plan(plan: SavedPlan, format='json') -> bytes:
    if format == 'json':
        result = dumps(plan)
    else:
        require(format == 'csv', 'PLAN_FORMAT', 'Use JSON or CSV')
        buffer = io.StringIO(newline='')
        writer = csv.writer(buffer)
        writer.writerow(('kind','key','value'))
        data = json.loads(dumps(plan))
        for key, value in data.items():
            # A literal apostrophe makes every value inert in spreadsheet applications.
            writer.writerow(('plan', key, "'" + json.dumps(value, ensure_ascii=False, separators=(',', ':'))))
        result = buffer.getvalue()
    payload = result.encode('utf-8')
    require(len(payload) <= MAX_PLAN_BYTES, 'PLAN_SIZE', 'Plan exceeds 256 KiB')
    return payload


def decode_plan(payload: bytes, catalog: Catalog, format='json') -> SavedPlan:
    require(type(payload) is bytes and len(payload) <= MAX_PLAN_BYTES, 'PLAN_SIZE', 'Plan exceeds 256 KiB')
    try:
        text = payload.decode('utf-8')
        if format == 'csv':
            reader = csv.reader(io.StringIO(text, newline=''), strict=True)
            require(next(reader) == ['kind','key','value'], 'PLAN_CSV', 'Unexpected CSV header')
            fields = {}
            for row in reader:
                require(len(row) == 3 and row[0] == 'plan' and row[2].startswith("'"), 'PLAN_CSV', 'Use an AionCrafter plan CSV export')
                require(row[1] not in fields, 'DUPLICATE_FIELD', 'CSV fields repeat')
                fields[row[1]] = row[2][1:]
            text = '{' + ','.join(json.dumps(k) + ':' + v for k, v in fields.items()) + '}'
        else:
            require(format == 'json', 'PLAN_FORMAT', 'Use JSON or CSV')
        plan = loads(SavedPlan, text)
        validate_plan(plan, catalog)
        return plan
    except (UnicodeError, csv.Error, StopIteration) as exc:
        from .codec import ValidationError
        raise ValidationError('PLAN_FORMAT', 'Malformed plan file') from exc


class PlanStore:
    """Separate user-plan database; immutable revisions and optimistic updates."""
    APPLICATION_ID = 0x41495032

    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        try:
            app = self.connection.execute('PRAGMA application_id').fetchone()[0]
            tables = self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            require(app == self.APPLICATION_ID or (app == 0 and not tables), 'PLAN_DATABASE', 'Choose a separate plan database')
            version = self.connection.execute('PRAGMA user_version').fetchone()[0]
            require(version <= 2, 'PLAN_VERSION', 'Plan database is from a newer application')
            with self.connection:
                # Serialize schema migration and seed counters from old revisions.
                self.connection.execute('BEGIN IMMEDIATE')
                self.connection.execute('CREATE TABLE IF NOT EXISTS plans (name TEXT, revision INTEGER, payload TEXT NOT NULL, PRIMARY KEY(name, revision))')
                self.connection.execute('CREATE TABLE IF NOT EXISTS plan_versions (name TEXT PRIMARY KEY, last_revision INTEGER NOT NULL)')
                self.connection.execute('INSERT OR IGNORE INTO plan_versions SELECT name, max(revision) FROM plans GROUP BY name')
                self.connection.execute(f'PRAGMA application_id={self.APPLICATION_ID}')
                self.connection.execute('PRAGMA user_version=2')
        except BaseException:
            self.connection.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.connection.close()

    def list(self):
        return tuple(self.connection.execute('SELECT name, max(revision) FROM plans GROUP BY name ORDER BY name').fetchall())

    def load(self, name, catalog):
        row = self.connection.execute('SELECT revision, payload FROM plans WHERE name=? ORDER BY revision DESC LIMIT 1', (name,)).fetchone()
        require(row is not None, 'PLAN_NOT_FOUND', 'Saved plan not found')
        return row[0], decode_plan(row[1].encode(), catalog)

    def save(self, plan, catalog, expected_revision=0):
        validate_plan(plan, catalog)
        require(type(expected_revision) is int and expected_revision >= 0, 'PLAN_REVISION', 'Revision must be nonnegative')
        payload = encode_plan(plan).decode()
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            row = self.connection.execute('SELECT max(revision) FROM plans WHERE name=?', (plan.name,)).fetchone()
            current = row[0] or 0
            require(current == expected_revision, 'CONCURRENT_CHANGE', 'Plan changed; reload before saving')
            last = self.connection.execute('SELECT last_revision FROM plan_versions WHERE name=?', (plan.name,)).fetchone()
            revision = (last[0] if last else 0) + 1
            self.connection.execute('INSERT INTO plans VALUES (?,?,?)', (plan.name, revision, payload))
            self.connection.execute('INSERT INTO plan_versions VALUES (?,?) ON CONFLICT(name) DO UPDATE SET last_revision=excluded.last_revision',
                                    (plan.name, revision))
        return revision

    def delete(self, name, expected_revision):
        require(type(expected_revision) is int and expected_revision > 0, 'PLAN_REVISION', 'Revision must be positive')
        with self.connection:
            self.connection.execute('BEGIN IMMEDIATE')
            row = self.connection.execute('SELECT max(revision) FROM plans WHERE name=?', (name,)).fetchone()
            require(row[0] is not None and row[0] == expected_revision, 'CONCURRENT_CHANGE', 'Plan changed; reload before deleting')
            # Keep only the per-name counter so recreation cannot revive stale tabs.
            self.connection.execute('DELETE FROM plans WHERE name=?', (name,))
