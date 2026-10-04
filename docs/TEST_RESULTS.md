# Phase 01 — executed validation

Date: 2026-10-04. Environment: Linux, Python 3.12.14; SQLite via standard library.
No external dependencies installed. All market/catalog data used is SYNTHETIC.

## Application checks

Command: `python3 -m unittest discover -v`

Result: **47 tests passed**, zero failures/errors (0.788 seconds in the recorded run).

| Suite | Tests | Evidence |
|---|---:|---|
| Identity | 8 | Stable JSON round-trip, variant/market/currency separation, unknown scope and cross-region rejection, attribute canonicalization, strict types. |
| Catalog | 12 | Fixture import, bilingual alias search/disambiguation, orphans, duplicate identities/recipes, cycles, scope/rights, malformed/oversized input. |
| Models | 11 | Exact amounts and negative result values, invalid inputs, joint/failure outcomes, exact probability sums under low Decimal precision, trade restrictions, source time/nulls. |
| SQLite storage/migrations | 14 | Reopen, migrations 1 to 2, immutable records, foreign references, rollback, simulated write failure, stale-writer rejection, checksum verification. |
| CLI | 2 | Actual subprocess validate/import/inspect, invalid import preserves the catalog, inspecting an absent DB does not create it. |

Command: `python3 -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json`

Result: release `SYNTHETIC-demo-v1`, 7 item variants, 3 recipes; dataset kind SYNTHETIC.
The CLI integration test also executes import and inspect against temporary SQLite.
The transaction test injects a SQLite trigger failure; it does not simulate an OS crash.
The concurrency test uses two database connections with a stale expected release ID.

## Documentation and archive

The untouched recovered bootstrap passed `python3 scripts/validate_bootstrap.py`
before the baseline commit: 7 phases, 42 IDs, 14 original artifact checksums.
The validator was then updated to permit evidenced implementation completion and
check the compatible roadmap progress sidecar against the backlog. The final
checkpoint receipt records the post-change document/manifest validation outcome.
The original bilingual HTML SHA-256 remains
`0881ff82158428f87fa5ed52d47ea601d4bd5665d116a179c49b3f04d623ec87`.

## Not tested or claimed

No real catalog correctness/rights validation, authenticated price response, provider
permission, game-client behavior, overlay, UI, production calculation engine, remote
CI or deployment. No claim of live-price freshness. Tests run on
Linux only; Windows/macOS runtime behavior remains untested.

## GitHub delivery revalidation (Part 02)

Re-ran all three commands on 2026-10-04 before upload: **47 tests passed** in 0.765
seconds, document validation passed all 36 then-current checksums, and fixture
validation reported 7 SYNTHETIC variants / 3 recipes. Remote implementation tree
`bb2146a339f3cc6b10eb473e50e364a9203d8aec` exactly matches the tested local tree.
The subsequent delivery update changes documentation/manifest only; application code
and tests are unchanged. GitHub PRs #1 and #2 are now open and unmerged.

## Phase 02 Part 01 — 2026-10-04

Runtime: Linux, Python 3.14.7. Actual fetched Phase 01 baseline
3a395eb5894e65ff0d67e336d1a91dc452136843 passed 47 tests.
Pure economics checkpoint passed 55; final workflow implementation passed 62:
`python3 -m unittest discover -q` (zero failures/errors, 2.057 seconds final run).
Nine economics tests cover the brief's fictional regression, batches/leftovers and
fee bases, missing values, zero-cost ROI, full tax, losses/rounding/minimal break-even,
large amounts under tiny Decimal context, price semantics/scope/duplicates and
unknown/invalid/equivalent deterministic probability inputs. Six manual tests cover
observation timestamps/missing/source, pasted ambiguity, materials-only/no sale fields,
item margins/non-determinism, picker/HTML escaping, and HTTP GET/POST/403/413.
Loopback HTTP tests ran with sandbox escalation because sandbox sockets were denied.
Initial test failures used the wrong alias for ambiguity; corrected to synthetic
potion and reran successfully. No skipped tests.

`python3 -m compileall -q aioncrafter` and offline catalog validation passed.
`python3 scripts/validate_bootstrap.py` passed after manifest refresh.
Fetched published checkpoints; exact tested local/remote trees matched.
Inherited SQLite ResourceWarnings remain on Python 3.14 (observed before changes).
Browser open was denied because admin-enforced policy verification was unavailable;
visual/layout/focus QA has not passed. No remote CI, real pilot/game/provider/overlay,
Windows, persistence or historical-ledger acceptance tests performed.

## Phase 02 Part 02 — 2026-10-04

Full suite: `python3 -m unittest discover -q` — 77 passed in 2.412 seconds.
Then strengthened the HTTP import-to-save timestamp preservation assertion and ran
`python3 -m unittest tests.test_plans -q` — 7 passed in 0.234 seconds.
6 valuation tests cover inventory aggregation/capping, replacement versus cash, missing
references, complete/partial/overallocated records, currencies/scopes and invalid input.
7 plan tests cover JSON/CSV round-trip, formula neutralization, rejected import preserving
existing state, reopen/revisions/conflicts/deletion, original observation timestamps,
malformed/forged plans, database-version isolation and HTTP lifecycle/CSRF.
Manual tests now include inventory/recorded views and bilingual product search.
Compileall, offline catalog validation, diff whitespace and bootstrap manifest checks
passed. Published implementation 4594c5a6c825733bd49c56c14cddfd41a3161ab7 was fetched
and matched the tested local tree. No new browser visual, pilot/game, provider/overlay,
Windows or remote CI tests. Inherited Python 3.14 SQLite ResourceWarnings remain.

## Phase 02 Part 03 — cloud continuation (2026-10-04)
Linux / Python 3.12.14. Full suite: 85 tests passed. Eight added tests cover six
reference/HTTP/round-trip/default-time/permission cases and two broader fee/joint-output
cases. Compileall, offline synthetic catalog validation (7 items/3 recipes), diff check
and refreshed bootstrap manifest validation passed. Browser visual QA remains unverified:
Playwright executable absent; Chromium install failed with invalid ZIP archives.
Inherited Python 3.14 SQLite ResourceWarnings remain unresolved; runtime differs here.
No pilot/game/provider/overlay/Windows or remote-CI success claimed.

## Phase 02 Part 03 — acceptance continuation (2026-10-04)

Python 3.12.14 / Linux. Reproduced stale-save bug: delete/recreate reset revision 1,
allowing the old revision-1 writer. Database v2 fixes it with persistent per-name counters.
Actual targeted run: `python3 -m unittest tests.test_form_acceptance tests.test_plans -q`
— 13 passed. Full run: `python3 -m unittest discover -q` — 91 passed, 2.989 seconds.
Four new complete-form HTTP cases verify both workflows, repeated calculate/search/save,
unknown-age snapshot + old vendor reference, linked override and CSV import-copy, and
atomic refusal of merged observation-ID collisions. Two storage regressions verify
v1→v2 migration without payload changes and stale save/delete rejection after recreation.
Compileall, offline catalog validation, diff check and refreshed bootstrap validation
passed. Connected cloud browser attempted the running loopback app and returned
`net::ERR_BLOCKED_BY_CLIENT`. Visual QA remains unverified; no screenshot obtained.
See PHASE_02_ACCEPTANCE.md; inherited Python 3.14 warnings remain unresolved there.

## Phase 02 to Phase 04 sequencing handoff — 2026-10-04

Reran the fetched baseline 91a2479c94a26757fc34ca09bac1e9218ff82935:
`python3 -m unittest discover -q` — 95 passed in 3.664 seconds (Python 3.12.14).
Only documentation/sequencing changes follow this baseline; no application changes.
ADR 0005 removes cloud/Chromium work from the active development queue and authorizes
Phase 04 synthetic engineering using Phase 02. Pending acceptance remains recorded.
Bootstrap manifest/42-ID validation and git diff --check passed after refreshing docs.

## Phase 02 owner clarification — 2026-10-04

Documentation-only update from verified 48dc8a304a9f917aec9caec27d62bd95041df530.
Recorded the user's review, behaviour acceptance and final-pilot timing; code is unchanged.
The existing 95-test baseline still applies; it was not rerun for these prose changes.
Refreshed manifest validation and git diff --check are the applicable checkpoint checks.

## Phase 03 starter preparation — 2026-10-04

Documentation-only from Phase 02 1bea9e9d687458eb78921fee31a979a568cbe3ae.
Fetched main 81f6493999b6bca1e86cd621e7815f7d05944020; git diff lists docs only
between it and Phase 02. No new application tests; previous 95-test baseline retained.
Checkpoint validation: refreshed artifact manifest, 42 stable IDs and git diff --check.
No Phase 03 feature, new-chat startup or external gate pass is claimed.

## Phase 03 Part 01 — freshness (2026-10-04)

Windows, bundled Python 3.12.14. `python` below means the bundled executable (not on PATH).
Baseline `python -m unittest discover -q`: 95 run, 2 existing migration cleanup errors
(Windows file locks). Fixed tests/test_storage.py transaction contexts to close connections.
`python -m unittest tests.test_price_cache -q`: 11 passed.
`python -m unittest discover -q`: 106 passed after that test-only correction.
Synthetic provider/clock; no real provider, browser/game, remote CI or Gate A evidence.

## Phase 03 Part 01 — resilience and depth (2026-10-04)

Windows/Python 3.12.14. `python` denotes the bundled executable at
`C:/Users/AngelTorresBarros/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
- `python -m unittest tests.test_price_cache tests.test_price_service tests.test_acquisition tests.test_market_groundwork -q`: **42 passed**.
- `python -m unittest discover -q`: **137 passed**, final rerun.
- `python -m compileall -q aioncrafter tests`: passed.
- `python -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json`: passed, 7 variants / 3 recipes, SYNTHETIC.
- `git diff --check` / staged diff check: passed.

One intermediate full run failed in unchanged test_http_get_post_and_size_origin_limits
with Windows ConnectionResetError while testing rejected Origin. Isolated rerun passed,
then the full suite passed. No production HTTP fix is claimed; record intermittent behavior.
Earlier baseline migration cleanup errors were fixed in test fixtures only.

42 Phase 03 tests comprise 11 cache, 17 service, 13 acquisition and 1 combined contract test.
The acquisition oracle enumerates 60 deterministic small mixed books. All tests use
synthetic observations and injected clock/provider; no real network transport or sleeps
in the Phase 03 tests. Existing form tests use loopback HTTP. This is not visual QA,
real-market reconciliation, a live integration, remote CI or Gate A acceptance.

## Phase 03 Part 02 — fallback history and retry budgets (2026-10-04)

Windows / bundled Python 3.12.14; same executable path as Part 01.
Five new regression cases failed on the unchanged implementation before correction:
manual mutation between calls, reuse of replaced provider IDs, duplicate manual IDs across
identities, provider mutation of a manual ID, and premature exhaustion in a mixed retry batch.
Twelve new regression tests now cover both defects and their atomicity/quota/reset boundaries.

- `python -m unittest tests.test_price_cache tests.test_price_service tests.test_acquisition tests.test_market_groundwork -q`: **54 passed** (13/27/13/1).
- `python -m unittest discover -q`: **149 passed**, no failures on this run.
- `python -m compileall -q aioncrafter tests`: passed.
- `python -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json`: passed, 7 variants / 3 recipes.
- `git diff --check`: passed; bootstrap/checksum results follow in delivery receipt.

No real provider, UI activation, browser QA, remote CI or real-game validation. Part 01's
intermittent Windows HTTP rejection-test reset is not claimed fixed by these changes.
