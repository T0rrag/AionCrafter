# AionCrafter — manual-edition engineering preview

A local, provider-independent crafting calculator with exact money, explicit missing
prices, recursive batches, bounded buy/craft comparisons, one-attempt scenarios and
an optional FIFO actual-results ledger. Bundled data is **SYNTHETIC ONLY**.

Active work: **Phase 06, Part 01 — validation and recovery**. The manual edition is
not released. Real catalog/market integration remains incomplete, Phase 05 overlay is
deferred, and Gates A/B are UNVERIFIED. No game service is connected.

## Run locally

Requires Python 3.12 and standard-library SQLite; no pip install or credentials.
From this directory (Windows launcher users can use `py -3.12`):

```text
python -m unittest discover -q
python scripts/validate_bootstrap.py
python -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json
python -m aioncrafter.web --catalog tests/fixtures/SYNTHETIC-catalog-v1.json
```

Open `http://127.0.0.1:8765`. Use an explicit fictional market, `TEST` currency with
2 decimal places and a timestamp with timezone. Blank prices stay unknown. Materials
mode needs no recipe or selling price; item mode requires explicit fee/tax assumptions.
Save/load/export/import operate locally. The actual-records link opens the separate ledger.

Read the [manual operating guide](docs/MANUAL_EDITION_GUIDE.md) before upgrading or
backing up. It covers supported scope, installation, data retention, per-file SQLite
backup/restore and the exact plans/ledger paths. `check-database` and `backup` inspect
and copy supported databases without migrating the source or overwriting destinations.

## Contracts and evidence

- [Data identity and persistence](docs/decisions/0002-phase-01-data-contracts.md)
- [Offline price references](docs/REFERENCE_IMPORTS.md)
- [Recursive batches and bounded routes](docs/PHASE_04_CRAFTING.md)
- [Scenarios, conditional rankings and actual records](docs/PHASE_04_SCENARIOS_AND_LEDGER.md)
- [Phase 06 validation and release matrix](docs/PHASE_06_VALIDATION.md)
- [Executed test results](docs/TEST_RESULTS.md)

Tax, probabilities, eligibility and rounding are explicit assumptions until supported
by real evidence. Source time never becomes newer merely because a record is reloaded.
Unsold stock is not realized revenue. Synthetic tests are not real-game acceptance,
browser visual QA, a remote CI pass or permission to enable automatic prices.

## Continue development

Fetch actual remote heads, then read [NEXT_CHAT_PROMPT](docs/NEXT_CHAT_PROMPT.md), its
immutable continuation, [PROJECT_STATE](docs/PROJECT_STATE.md), AGENTS.md and required
ADRs/backlog. GitHub is the durable recovery record; do not assume a previous chat's
SHA is the latest head. Phase 06 uses `phase/06-release` against `main`.

The original bilingual roadmap and its 42 IDs remain intact. Import
`docs/roadmap-progress.json` using its Import control to apply current completion
evidence. Export existing browser notes first: importing replaces them after confirmation.

Independent project; not affiliated with NC, Overwolf or CurseForge. No redistribution
license is currently declared; fixture attribution is in `docs/sources/SYNTHETIC.md`.
