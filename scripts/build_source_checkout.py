#!/usr/bin/env python3
"""Build a deterministic source-checkout validation archive.

The archive is an internal Phase 06 validation artifact, not a public release.
No redistribution license is inferred or added by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZIP_STORED, ZipFile, ZipInfo

ARCHIVE_ROOT = "AionCrafter-source"
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ROOT_ENTRIES = (
    ".gitattributes",
    ".github",
    ".gitignore",
    "AGENTS.md",
    "AionCrafter_Project_Prompt.md",
    "AionCrafter_Roadmap.html",
    "README.md",
    "aioncrafter",
    "docs",
    "scripts",
    "tests",
)
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
METADATA_PATH = f"{ARCHIVE_ROOT}/SOURCE_ARTIFACT.json"


def included_files(root: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for name in ROOT_ENTRIES:
        entry = root / name
        if not entry.exists():
            raise FileNotFoundError(f"required source entry is missing: {name}")
        candidates = (entry,) if entry.is_file() else entry.rglob("*")
        for path in candidates:
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part in SKIP_DIRS for part in relative.parts):
                continue
            if path.suffix in SKIP_SUFFIXES:
                continue
            files.append(path)
    return tuple(sorted(files, key=lambda p: p.relative_to(root).as_posix()))


def artifact_metadata() -> bytes:
    payload = {
        "artifact_kind": "source-checkout-validation",
        "format_version": 1,
        "license_status": "unresolved",
        "public_release": False,
        "python": ">=3.12",
        "scope": "SYNTHETIC/local validation only",
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def zip_info(path: str) -> ZipInfo:
    info = ZipInfo(path, FIXED_TIMESTAMP)
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def build_archive(root: Path, output: Path) -> str:
    root = root.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = included_files(root)
    entries = [(f"{ARCHIVE_ROOT}/{PurePosixPath(path.relative_to(root).as_posix())}", path.read_bytes())
               for path in files]
    entries.append((METADATA_PATH, artifact_metadata()))
    with ZipFile(output, "w") as archive:
        for archive_name, payload in sorted(entries, key=lambda item: item[0]):
            archive.writestr(zip_info(archive_name), payload)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    digest = build_archive(args.root, args.output)
    print(f"SOURCE_CHECKOUT_SHA256={digest}")
    print("LICENSE_STATUS=unresolved; artifact is validation-only and is not a public release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
