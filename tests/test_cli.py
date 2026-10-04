import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.helpers import FIXTURE


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "aioncrafter", *map(str, args)], capture_output=True, text=True)

    def test_offline_validate_import_inspect_and_invalid_import(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "sample.sqlite3"
            valid = self.run_cli("validate", FIXTURE)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertEqual(json.loads(valid.stdout)["dataset_kind"], "SYNTHETIC")
            imported = self.run_cli("import", FIXTURE, "--database", db)
            self.assertEqual(imported.returncode, 0, imported.stderr)
            inspected = self.run_cli("inspect", "--database", db)
            self.assertEqual(inspected.returncode, 0, inspected.stderr)
            invalid = Path(temp) / "bad.json"
            invalid.write_text('{"schema_version": 999}')
            failed = self.run_cli("import", invalid, "--database", db, "--expect-active", "SYNTHETIC-demo-v1")
            self.assertEqual(failed.returncode, 2)
            self.assertNotIn("Traceback", failed.stderr)
            self.assertEqual(self.run_cli("inspect", "--database", db).stdout, inspected.stdout)

    def test_inspect_missing_database_does_not_create_it(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "missing.sqlite3"
            result = self.run_cli("inspect", "--database", db)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(db.exists())
