"""Offline catalog validation/import/export commands; never contacts a provider."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

from .catalog import MAX_IMPORT_BYTES, import_catalog
from .codec import ValidationError, to_data
from .storage import Store
from .database import backup_database, check_database, export_catalog_release


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("file", type=Path)
    publish = sub.add_parser("import")
    publish.add_argument("file", type=Path)
    publish.add_argument("--database", required=True)
    publish.add_argument("--expect-active", help="Previous release ID; omit only for an empty database")
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--database", required=True)
    rollback = sub.add_parser("rollback")
    rollback.add_argument("release_id")
    rollback.add_argument("--database", required=True)
    rollback.add_argument("--expect-active", required=True)
    export = sub.add_parser('export-catalog', help='Export one validated stored catalog release to a new JSON file')
    export.add_argument('--database', required=True, type=Path)
    export.add_argument('--output', required=True, type=Path)
    export.add_argument('--release-id', help='Stored release to export; omit to export the active release')
    check = sub.add_parser('check-database', help='Read-only schema and SQLite integrity check; no migration')
    check.add_argument('--database', required=True, type=Path)
    backup = sub.add_parser('backup', help='Verified per-file SQLite backup to a new path; never overwrites')
    backup.add_argument('--database', required=True, type=Path)
    backup.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'check-database':
            result = check_database(args.database)
        elif args.command == 'backup':
            result = backup_database(args.database, args.output)
        elif args.command == 'export-catalog':
            result = export_catalog_release(args.database, args.output, args.release_id)
        elif args.command in ("validate", "import"):
            with args.file.open("rb") as stream:
                catalog = import_catalog(stream.read(MAX_IMPORT_BYTES + 1))
            result = {"release_id": catalog.release_id, "dataset_kind": catalog.scope.dataset_kind.value,
                      "items": len(catalog.items), "recipes": len(catalog.recipes)}
            if args.command == "import":
                with Store(args.database) as store:
                    result["changes"] = to_data(store.publish(catalog, expected_active=args.expect_active))
        else:
            if not Path(args.database).is_file():
                raise ValidationError("DATABASE_NOT_FOUND", args.database)
            with Store(args.database) as store:
                if args.command == "rollback":
                    store.rollback(args.release_id, expected_active=args.expect_active)
                catalog = store.catalog()
                result = {"active_release_id": catalog.release_id, "dataset_kind": catalog.scope.dataset_kind.value,
                          "items": len(catalog.items), "recipes": len(catalog.recipes)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValidationError, OSError, sqlite3.Error) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
