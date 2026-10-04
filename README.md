# AionCrafter — manual calculator and data foundation

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

Phase 02 adds a local web calculator with manually entered prices, inventory-aware
costs and versioned saved plans alongside the data-foundation CLI/library.
Its engineering work can use labeled synthetic fixtures while the real-catalog task
remains blocked. Automatic prices and overlay are deferred (ADR 0003).

## Project records

Read `docs/PROJECT_STATE.md`, `docs/backlog.json`,
`docs/handoffs/phase-04-part-02.md` and `docs/NEXT_CHAT_PROMPT.md` before continuing.
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

## Phase 02 — local manual calculator

```bash
python3 -m aioncrafter.web --catalog tests/fixtures/SYNTHETIC-catalog-v1.json
```

Open `http://127.0.0.1:8765` in your browser. Enter an explicit synthetic market ID,
faction mode, currency code/precision and ISO 8601 observation time with timezone.
The bundled fixture uses `TEST` with 2 decimal places for its synthetic craft fees.
Enter unit prices manually; blank means unavailable. Materials mode needs quantities
or pasted `quantity<TAB>exact alias` rows, with a variant picker for ambiguous names.
Item mode needs product, recipe, planned selling quantity, selling price and explicit
sale-fee/tax assumptions. A craft-fee override is optional; blank uses catalog fees,
including unknown fees. A zero override explicitly waives the fee for this estimate.

This local HTTP server binds to loopback. Saved plans persist prices, favorites, market
settings, inventory and recorded material costs in `local-data/plans.sqlite3` (override
with `--plans PATH`). Keep this user database private; back it up before upgrades.
Load a named plan before updating it; concurrent stale saves fail instead of overwriting.
JSON/CSV exports are lossless AionCrafter plan bundles tied to the exact catalog digest.
CSV cells are neutralized against spreadsheet formulas. Paste exports into Import for
a validated preview, then save. Reset clears unsaved inputs; deleting a named plan and
its revisions requires the explicit confirmation checkbox. Deterministic
direct ingredients only; unknown proc probabilities are refused. Unsold leftovers and
coproducts receive no credited revenue. ROI/unrounded break-even use exact rational
arithmetic; displayed monetary results use exact currency units and chosen proceeds
rounding. Fees and rounding are unverified assumptions, not game rules.

[Phase 02 draft PR #3](https://github.com/T0rrag/AionCrafter/pull/3) is stacked on PR #2.
91 local tests pass, including complete-form HTTP and plan migration regressions. Browser
visual QA remains unverified: local Chromium is unavailable and the cloud browser blocks
the loopback URL. Phase 02 remains IN_PROGRESS; see the current state and handoff.

Part 02 adds owned-quantity inputs and optional historical material-cost allocations.
Replacement value still includes owned inputs; additional cash uses only missing units
and known craft fees. Recorded material cost requires coverage for every consumed unit
and a record reference. It excludes historical crafting/sale fees and realized profit.
Product search matches English/Spanish aliases without accents. Part 03 adds validated
offline manual/vendor/snapshot reference imports and per-item source/age labels. Exact
observations survive calculate/search/save and JSON/CSV transfers. See
[reference imports](docs/REFERENCE_IMPORTS.md) and [acceptance evidence](docs/PHASE_02_ACCEPTANCE.md).

Plan database v2 upgrades existing v1 databases automatically without changing plan
payloads. Revision numbers remain increasing when a name is deleted and recreated, so
stale tabs cannot overwrite/delete the recreated plan. Only its name/revision counter
survives deletion. Older v1-only applications refuse the upgraded database; keep a backup
before upgrading. JSON/CSV plan schema remains v1.

Phase 04 Part 01 adds recursive crafting and bounded buy/craft cost comparisons.
See [crafting contracts](docs/PHASE_04_CRAFTING.md) for usage and limitations.

Phase 04 Part 02 adds one-attempt scenarios, conditional route rankings and an optional
actual-results ledger. In the crafting workflow choose `scenarios` or `rank`; the
**Record actual purchases, crafts and sales** link opens the separate local ledger.
See [usage and evidence limits](docs/PHASE_04_SCENARIOS_AND_LEDGER.md). No provider or game
connection is added; historical profit needs actual records, never a guessed cost basis.
