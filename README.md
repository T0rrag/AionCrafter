# AionCrafter — Phase 01 data foundation

Provider-independent Python contracts, catalog validation and SQLite persistence
for an external AION 2 crafting companion. Current data is **SYNTHETIC ONLY**.
Phase 01 is **IN_PROGRESS**: the permitted real catalog is blocked. Automatic live
prices (Gate A) and overlay support (Gate B) are **UNVERIFIED**.

## Run locally

Requires Python 3.12 with standard-library SQLite. No pip install or credentials.
Run from this directory (Windows: use `py -3.12` instead of `python3`):

```bash
python3 -m unittest discover -v
python3 scripts/validate_bootstrap.py
python3 -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json
python3 -m aioncrafter import tests/fixtures/SYNTHETIC-catalog-v1.json --database demo.sqlite3
python3 -m aioncrafter inspect --database demo.sqlite3
```

The first import expects an empty database. For later imports pass
`--expect-active SYNTHETIC-demo-v1` (using the actual previous release ID). Each
changed dataset needs a new `release_id`; identical retries are allowed.
The import prints changes to item and recipe identities/metadata for review.
Rollback an existing later release with:

```bash
python3 -m aioncrafter rollback SYNTHETIC-demo-v1 --database demo.sqlite3 --expect-active SYNTHETIC-demo-v2
```

The example v2 ID is illustrative; it must exist before that command can succeed.
For a fresh demo, use a new database filename. SQLite files are local user data and
ignored by Git. Back them up before upgrading; unsupported newer schemas fail closed.

## Included

- Stable item/variant/market/currency identities and explicit unknown states.
- Strict versioned JSON; bilingual search aliases with explicit disambiguation.
- Recipe batches, joint outcomes/failure, unknown probabilities and fee metadata.
- Bound/tradeable variants, acquisition restrictions and price semantics.
- Validation for duplicates, aliases, orphan references, cycles, scopes and rights.
- Immutable SQLite catalog releases, migrations, observations and calculation records;
  transactional publication, concurrent-write checks, review diffs and rollback.
- Separate typed catalog/price provider protocols. No provider implementation connects
  to a game service. Missing prices remain null and timestamps retain provenance.

This is a data-foundation CLI/library, not yet the player-facing calculator. Phase 02
will add calculations and UI after review of this phase and its remaining data blocker.

## Project records

Read `docs/PROJECT_STATE.md`, `docs/backlog.json`,
`docs/handoffs/phase-01-part-01.md` and `docs/NEXT_CHAT_PROMPT.md` before continuing.
`docs/decisions/0002-phase-01-data-contracts.md` documents the engineering choices.
`docs/TEST_RESULTS.md` records actual local validation and its limits.
`docs/GITHUB_DELIVERY.md` retains the publishing procedure; `docs/PHASE_01_PR.md`
is the prepared draft description, not an opened PR.

The original EN/ES roadmap remains byte-for-byte intact, with all 42 task IDs and
existing browser notes/progress behavior. Import `docs/roadmap-progress.json` through
its existing Import control to apply this checkpoint. Export your browser's current
notes first because that existing control replaces progress and notes after confirmation.
`docs/backlog.json` is the detailed task-status/evidence record.

## GitHub and checkpoint

Target: `T0rrag/AionCrafter`; remote access currently returns 404. Both local branches
are included in the checkpoint's Git bundle. The Phase 01 branch is stacked on
`phase/00-architecture-bootstrap`; nothing is merged, deployed or published remotely.
See the package's `CHECKPOINT_RECEIPT.json` for exact local SHAs. A local SHA is not
proof of a GitHub upload. Publish only after inspecting the actual remote base.

Independent project; not affiliated with NC, Overwolf or CurseForge.
