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
