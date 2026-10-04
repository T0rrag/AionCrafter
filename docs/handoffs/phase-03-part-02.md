# Phase 03 / Part 02 — Immutable fallback history and independent retry budgets

2026-10-04 · Brief v1.3 / ADR 0006 · Phase IN_PROGRESS.
Repository T0rrag/AionCrafter, branch phase/03-market-prices, draft PR #5 against main.
Started from verified remote bb967e63e51add0649d523aca00c3764d6b58bf6 with a clean checkout.
Main remains 81f6493999b6bca1e86cd621e7815f7d05944020; no stacked PR dependency.
This same Aion2 Phase 03 chat remains the only active writer. No new chat was created.

## Changes and evidence

No new authorized provider evidence was found in repository/project sources or PR #5
comments (empty). Continued provider-independent contract review without real connection.
Five newly added regression cases failed before fixes, demonstrating two defects:

- p3-resilience: a retryable batch containing identities with different prior attempt
  counts exhausted all members when just one hit its limit. Exhaustion is now per identity.
  Newer members keep a retry time; provider cooldown, Retry-After and quota still apply.
  Permanent errors still exhaust every affected member, regardless of its attempt count.
- p3-freshness/p3-resilience: manual fallback checked only the current cache entry, allowing
  an existing ID to be mutated across requests or reused from replaced provider history.
  PriceCache now atomically validates/reserves IDs for both manual and provider records.
  Rejected selections reserve nothing, identical replay is allowed, retry reset keeps
  immutable history, and manual selection never replaces the provider cache entry.

Code: price_cache.py and price_service.py. Twelve new regression tests include mixed
retry/quota cases, cross-origin/cross-identity ID collisions and atomic rejection. No
changes to acquisition arithmetic, calculator behavior or transport activation.

## Validation actually executed

Windows / bundled Python 3.12.14; bare python is not on PATH. Commands below use the
bundled executable under ~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python.
`python -m unittest tests.test_price_cache tests.test_price_service tests.test_acquisition
 tests.test_market_groundwork -q`: 54 passed (13 cache, 27 service, 13 depth, 1 combined).
`python -m unittest discover -q`: 149 passed. No failure on this full-suite run.
`python -m compileall -q aioncrafter tests`: passed.
`python -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json`: passed,
7 variants / 3 recipes. Diff checks passed; refreshed bootstrap manifest validation
preserves all 42 task IDs. No visual, remote CI, game or provider acceptance claim.
Part 01's intermittent Windows HTTP reset remains documented; this change does not fix it.

## Remaining work and continuation

Phase 03 and p3-freshness/resilience/depth IN_PROGRESS. The cache/service remain single-owner
in-memory groundwork: production shared quota/cache ownership, transport timeout/cancellation,
application integration and real-market acceptance remain pending. ID history is instance-local;
persistent Store retains its separate immutable-history contract. No retention/eviction change.
p3-adapter/reconcile/releaseprice BLOCKED; Gates A/B UNVERIFIED. Synthetic tests cannot pass
Gate A or real market reconciliation. p1-catalog BLOCKED, Phase 05 DEFERRED. Phase 02 behavior
accepted; visual QA deferred; game pilot after phase feature work. No Chromium work.

Next continuation: fetch the actual head, read PROJECT_STATE, this handoff, PHASE_03_GROUNDWORK,
backlog, ADR 0006 and the delivery receipt. Inspect authorization/scoped provider evidence
before any real integration. Without it, retain blockers; do not invent a provider or activate
prices. Keep the same branch/PR and one writer; Phase 04 requires its own chat. No merge or
force-push. Publication SHA/tree verification is recorded in the delivery receipt after upload.
