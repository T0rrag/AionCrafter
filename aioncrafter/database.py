"""Offline database recognition and per-file SQLite snapshots; no migrations."""
from contextlib import closing
import hashlib
from pathlib import Path
import sqlite3
import time

from .codec import require

CATALOG_APPLICATION_ID = 0x41494331
PLAN_APPLICATION_ID = 0x41495032
LEDGER_APPLICATION_ID = 0x41494C34
CATALOG_V1 = {
    'catalog_releases': ('release_id', 'digest', 'payload'),
    'active_catalog': ('singleton', 'release_id'),
}
CATALOG_V2 = dict(CATALOG_V1, observations=('observation_id', 'release_id', 'price_key', 'supersedes_id', 'payload'),
                  calculations=('calculation_id', 'release_id', 'payload'))
PLAN_V1 = {'plans': ('name', 'revision', 'payload')}
PLAN_V2 = dict(PLAN_V1, plan_versions=('name', 'last_revision'))
LEDGER_V1 = {'journals': ('name', 'revision', 'payload')}


def schema_matches(connection, expected):
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if tables != set(expected):
        return False
    # Only constant, recognized table names are interpolated.
    return all(tuple(row[1] for row in connection.execute(f'PRAGMA table_info({table})')) == columns
               for table, columns in expected.items())


def database_info(connection):
    """Check structure/integrity, not catalog rights or application payload semantics."""
    app = connection.execute('PRAGMA application_id').fetchone()[0]
    version = connection.execute('PRAGMA user_version').fetchone()[0]
    known = (
        ('catalog', (0, CATALOG_APPLICATION_ID), {1: CATALOG_V1, 2: CATALOG_V2}),
        ('plans', (PLAN_APPLICATION_ID,), {1: PLAN_V1, 2: PLAN_V2}),
        ('ledger', (LEDGER_APPLICATION_ID,), {1: LEDGER_V1}),
    )
    kind = next((name for name, apps, versions in known if app in apps and version in versions
                 and schema_matches(connection, versions[version])), None)
    require(kind is not None, 'DATABASE_SCHEMA', 'Unrecognized or unsupported database; no migration performed')
    require(connection.execute('PRAGMA integrity_check').fetchall() == [('ok',)],
            'DATABASE_INTEGRITY', 'SQLite integrity check failed')
    require(not connection.execute('PRAGMA foreign_key_check').fetchall(),
            'DATABASE_INTEGRITY', 'SQLite foreign-key check failed')
    return {'kind': kind, 'schema_version': version, 'application_id': app,
            'sqlite_integrity': 'ok', 'payload_validation': 'not_performed'}


def _readonly(path):
    path = Path(path).resolve()
    require(path.is_file(), 'DATABASE_NOT_FOUND', 'Database file does not exist')
    return sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)


def check_database(path):
    with closing(_readonly(path)) as connection:
        return database_info(connection)


def backup_database(source, destination):
    """Copy a consistent SQLite snapshot to a NEW file, refusing any overwrite.

    Each invocation covers one file. Stop writers before backing up a related set.
    The digest identifies the backup bytes, not a promise of source-byte equality.
    """
    destination = Path(destination)
    created = False
    try:
        with closing(_readonly(source)) as original:
            database_info(original)
            # SQLite may consume/delete orphaned journals even when the main file
            # does not exist. Preserve all pre-existing recovery data at this path.
            for suffix in ('-wal', '-shm', '-journal'):
                sidecar = Path(str(destination) + suffix)
                require(not sidecar.exists() and not sidecar.is_symlink(), 'BACKUP_DESTINATION',
                        'Destination has SQLite sidecars; choose a new path')
            # Exclusive creation also rejects same-file aliases and existing empty files.
            with destination.open('xb'):
                created = True
            deadline = time.monotonic() + 30

            def progress(status, remaining, total):
                require(time.monotonic() < deadline, 'BACKUP_BUSY', 'Backup timed out; stop writers and retry')

            with closing(sqlite3.connect(destination)) as copy:
                original.backup(copy, pages=256, progress=progress, sleep=0.05)
                require(copy.execute('PRAGMA journal_mode=DELETE').fetchone()[0] == 'delete',
                        'BACKUP_JOURNAL', 'Backup must be a standalone database')
                info = database_info(copy)
        with destination.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        return dict(info, sha256=digest, bytes=destination.stat().st_size)
    except BaseException:
        if created:
            destination.unlink(missing_ok=True)
        raise
