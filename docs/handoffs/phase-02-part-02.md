# AionCrafter — Phase 02 / Part 02 handoff

Date: 2026-10-04. Brief v1.3; ADR 0003 and new ADR 0004.
Phase 02 IN_PROGRESS. Branch phase/02-manual-calculator, draft PR #3 stacked on PR #2.
Implementation SHA: 4594c5a6c825733bd49c56c14cddfd41a3161ab7.
Original Phase 01 base remains 3a395eb5894e65ff0d67e336d1a91dc452136843.

## Delivered and verified

Recovered accessible architecture, Phase 01, its executor, Phase 02 and related
translation chat context; inspected archived listings, Pages search and repository.
No permitted catalog was recovered. Prior workbook copy/download/print restrictions
and failed export do not authorize application reuse. Retain SYNTHETIC fixtures.

User explicitly authorized autonomous continuation and new chats in the same Aion2
project at phase boundaries or when context grows too large. ADR 0004 records this
change, published at 9fc281362bf0485fd4b3e28651e715443989dbaa. An attempted local Part 02
chat creation was rejected: Aion2 is a ChatGPT project, requiring cloud Work. No new
chat was created. A cloud-execution clarification was requested; no answer received
at this checkpoint. Continued eligible local work without waiting.

p2-costmodes increment: valuation.py consumes owned inventory once after demand
aggregation. Replacement cost remains unchanged; additional cash reflects only units
to buy, plus known assumed craft fees in item mode. Explicit historical allocations
report recorded consumed-material cost only when records cover all required units.
Partial records stay unknown; over-allocation, wrong market/currency, duplicate
inventory and invalid quantities fail validation. No realized profit is inferred.

p2-save increment: plans.py provides a separate local SQLite database with immutable
plan revisions, optimistic writes, favorites, settings, manual prices, inventory and
historical allocations. Catalog release plus content digest protects index-based form
fields from silent remapping. JSON and formula-neutralized CSV round-trip validated
plans. Import previews before saving; reset clears only the unsaved form; named plan
deletion requires explicit confirmation and expected revision. Original observations
survive reload/import/save; edits create linked new IDs. Old revisions retain history.

web.py integrates these features and bilingual alias product search. Storage mutations
require the page CSRF token; Host/Origin checks constrain the loopback app. Load/export/
reset/import controls can be used from a blank form without unrelated required fields.
Run python3 -m aioncrafter.web --catalog tests/fixtures/SYNTHETIC-catalog-v1.json;
plans default to ignored local-data/plans.sqlite3 (override with --plans).

## Actual validation

Full suite: python3 -m unittest discover -q — 77 passed. After strengthening the
import/save provenance assertion: python3 -m unittest tests.test_plans -q — 7 passed.
compileall and offline synthetic catalog validation passed. git diff --check passed.
Bootstrap checksum/task validator passed after refreshing the manifest. The remote
implementation was fetched and git diff --exit-code confirmed exact tested tree equality.
Linux / Python 3.14.7. Inherited SQLite ResourceWarnings remain. No new visual browser,
real pilot/game, provider, overlay, Windows or remote CI verification is claimed.

## Remaining work and next action

All six Phase 02 tasks remain IN_PROGRESS pending acceptance, broader fee/joint-output
coverage, source-aware approved reference imports/vendor/snapshot UI, explicit age
presentation and browser QA. Historical values cover allocated material cost; actual
craft/sale records and realized profit belong to later ledger work. Direct ingredients
are supported; recursive optimization remains Phase 04. Keep Phase 01 incomplete,
p1-catalog BLOCKED, Phases 03/05 DEFERRED and Gates A/B UNVERIFIED. No merge/force-push.

Continue Phase 02 Part 03 after reading PROJECT_STATE.md, backlog.json, this handoff,
ADR 0004, plans.py/valuation.py/web.py and tests. Resolve the pending cloud-chat choice
before claiming a new chat. If unavailable, continue eligible work locally and report
the routing limitation accurately. Fetch the current head; delivery docs follow code.
