from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from scripts.benchmark_cached_calculation import run_benchmark
from scripts.build_source_checkout import ARCHIVE_ROOT, METADATA_PATH, build_archive


class Phase06PackagePerformanceTests(unittest.TestCase):
    def test_source_checkout_archive_is_reproducible_and_smoke_validates(self):
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temp:
            temp = Path(temp)
            first = temp / "first.zip"
            second = temp / "second.zip"
            digest_a = build_archive(root, first)
            digest_b = build_archive(root, second)
            self.assertEqual(digest_a, digest_b)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with ZipFile(first) as archive:
                names = archive.namelist()
                self.assertEqual(names, sorted(names))
                self.assertIn(METADATA_PATH, names)
                metadata = json.loads(archive.read(METADATA_PATH))
                self.assertEqual(metadata["license_status"], "unresolved")
                self.assertFalse(metadata["public_release"])
                self.assertTrue(all("__pycache__" not in name and not name.endswith(".pyc") for name in names))
                archive.extractall(temp / "extract")
            extracted = temp / "extract" / ARCHIVE_ROOT
            completed = subprocess.run(
                [sys.executable, "-m", "aioncrafter", "validate", "tests/fixtures/SYNTHETIC-catalog-v1.json"],
                cwd=extracted,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("SYNTHETIC-demo-v1", completed.stdout)

    def test_cached_calculation_benchmark_uses_one_provider_fetch(self):
        result = run_benchmark(warmup=10, samples=50, target_p95_ms=300.0)
        self.assertEqual(result["dataset_kind"], "SYNTHETIC")
        self.assertEqual(result["provider_calls"], 1)
        self.assertEqual(result["samples"], 50)
        self.assertLess(result["latency_ms"]["p95"], 300.0)
        self.assertTrue(result["target_met"])


if __name__ == "__main__":
    unittest.main()
