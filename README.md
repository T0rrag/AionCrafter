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
is the next development chat: calculations and a web UI with manually entered prices.
Its engineering work can use labeled synthetic fixtures while the real-catalog task
remains blocked. Automatic prices and overlay are deferred (ADR 0003).

## Project records

Read `docs/PROJECT_STATE.md`, `docs/backlog.json`,
`docs/handoffs/phase-01-part-03.md` and `docs/NEXT_CHAT_PROMPT.md` before continuing.
`docs/decisions/0002-phase-01-data-contracts.md` documents the engineering choices.
`docs/TEST_RESULTS.md` records actual local validation and its limits.
`docs/GITHUB_DELIVERY.md` retains the publishing procedure; `docs/PHASE_01_PR.md`
records the published draft PR.

The original EN/ES roadmap remains byte-for-byte intact, with all 42 task IDs and
existing browser notes/progress behavior. Import `docs/roadmap-progress.json` through
its existing Import control to apply this checkpoint. Export your browser's current
notes first because that existing control replaces progress and notes after confirmation.
`docs/backlog.json` is the detailed task-status/evidence record.

## GitHub and checkpoint

Repository: https://github.com/T0rrag/AionCrafter

- [Architecture baseline — PR #1](https://github.com/T0rrag/AionCrafter/pull/1): open for review.
- [Phase 01 — PR #2](https://github.com/T0rrag/AionCrafter/pull/2): draft, stacked on the architecture branch.

The verified implementation commit is `703c7135539c69e639a5d75334ece19d55a8afe9`.
Current delivery documentation may follow it on `phase/01-data-foundation`.
See `docs/GITHUB_DELIVERY.md` for exact bases, tree comparisons and review boundaries.
The earlier repository-access blocker is resolved. Neither PR has been merged.

```bash
git clone --branch phase/01-data-foundation https://github.com/T0rrag/AionCrafter.git
cd AionCrafter
python3 -m unittest discover -v
```

Independent project; not affiliated with NC, Overwolf or CurseForge.
