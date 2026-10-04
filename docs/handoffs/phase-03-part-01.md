# Phase 03 / Part 01 — Market-price groundwork handoff

2026-10-04. Brief v1.3; ADR 0006. Phase IN_PROGRESS.
Repository T0rrag/AionCrafter; branch phase/03-market-prices; draft PR #5 against main.
Base 81f6493999b6bca1e86cd621e7815f7d05944020 verified before writes. Phase 03 did not exist.
Main contains calculator code equivalent to Phase 02 cb0ce5cb9227184300055f1df8bb415b2ef2515e;
current handoff/decisions were carried forward. No dependency on old draft PR #3.

## Delivered

p3-freshness: PriceCache preserves original records, source age and ingestion times, with
separate retrieval TTL, exact identity, unknown/future ages, immutable ID replay and atomic
validation. First published checkpoint 4d10338bf4e940f8929e062d8449d48e3499e340, tree
260bf1b58de02af779cfdf3b60334f98db5fdfd4, fetched and matched to tested files.

p3-resilience: PriceService and explicit batch protocol use configured quotas, bounded
attempts, backoff/Retry-After and shared cooldown. No sleeps or network; caller receives
retry_at. Exhaustion requires explicit reset without bypassing quota/cooldown. Failed
refreshes retain stale observations and errors. Explicit manual fallback preserves origin.

p3-depth: ListingOffer wraps the existing observation contract with exact total and explicit
partial-purchase support. Exact bounded search handles whole stacks and divisible listings,
returns leftovers/missing coverage, and rejects unsupported types/scopes/mixed snapshots.
Reference/minimum-only totals remain indicative with unverified stock. No live availability
promise or leftover resale credit. All examples/providers/fixtures SYNTHETIC ONLY.

## Tests actually run

Bundled Windows Python 3.12.14 (bare python not on PATH):
- `python -m unittest discover -q`: baseline 95 run with 2 pre-existing SQLite test-fixture
  cleanup errors; explicit closing fixed them. Freshness checkpoint: 106 passed.
- `python -m unittest tests.test_price_cache tests.test_price_service tests.test_acquisition
  tests.test_market_groundwork -q`: 42 passed (11 cache, 17 service, 13 depth, 1 combined).
- Final `python -m unittest discover -q`: 137 passed.
- `python -m compileall -q aioncrafter tests` and `python -m aioncrafter validate
  tests/fixtures/SYNTHETIC-catalog-v1.json`: passed (7 variants/3 recipes).
- Diff checks and refreshed `python scripts/validate_bootstrap.py` cover all 42 IDs.

60 small synthetic books match exhaustive optimum enumeration. Combined scenario verifies
cache/outage/manual/depth and immutable SQLite history. One intermediate full-suite run
had an existing HTTP rejection ConnectionResetError; isolated test and full rerun passed.
Intermittent Windows HTTP behavior remains a recorded limitation, not a fixed defect.

## Remaining work and continuity

p3-freshness/resilience/depth IN_PROGRESS: offline contracts implemented; real adapter,
shared production quota/cache ownership, transport timeout/cancellation, UI integration
and market acceptance remain. PHASE_03_GROUNDWORK.md records these boundaries.
p3-adapter/reconcile/releaseprice BLOCKED; Gate A/B UNVERIFIED. Permission and scoped
provider evidence precede any real connection. Synthetic tests cannot satisfy real
20-item/two-snapshot reconciliation. Phase 01 incomplete/p1-catalog BLOCKED; Phase 05 DEFERRED.
Phase 02 behavior accepted; visual QA deferred; game pilot after phase feature work.

Next Phase 03 continuation: fetch actual head, read PROJECT_STATE, this handoff, backlog,
ADR 0006, PHASE_03_GROUNDWORK and delivery receipt; inspect new external evidence first.
If none exists, retain blockers and review offline. Do not start Phase 04 here. One active
writer, same phase branch/PR, no merge/force-push. Receipts follow implementation; no
new-chat creation or automatic transcript synchronization is claimed.
