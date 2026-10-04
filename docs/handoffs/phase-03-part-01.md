# Phase 03 / Part 01 — Market-price groundwork

2026-10-04. Brief v1.3; ADR 0006. Phase IN_PROGRESS.
Repository: T0rrag/AionCrafter; branch phase/03-market-prices; base main at
81f6493999b6bca1e86cd621e7815f7d05944020. Verified remote heads before writes;
Phase 03 did not exist. Main and Phase 02 handoff cb0ce5 differ only in documentation.
PR #4 merged calculator code; PR #3 still draft/open. No stacked PR dependency.

First increment: p3-freshness, price_cache.py with 11 deterministic synthetic tests.
TTL uses retrieval time, source age uses observed_at, original fetched_at remains intact.
Unknown, unavailable, zero and empty results remain distinct. Exact full identity and
provider-local cache ownership prevent joins across variants/scopes/providers. Invalid
batch responses and changed observation IDs cannot overwrite last known-good data.
A clock rollback invalidates TTL and marks future source observations explicitly.

Baseline: Windows/Python 3.12.14 ran 95 tests with two existing Windows SQLite cleanup
errors. Fixed test-only connection lifetimes with contextlib.closing; production storage
already closes its connections. Full suite now 106 passed. Targeted cache suite: 11 passed.
Commands use the bundled Python executable; bare python is not on PATH.

Next in this same phase: p3-resilience configurable batching/quotas/bounded backoff and
explicit error/manual fallback, then p3-depth exact listing/whole-stack acquisition.
All data SYNTHETIC ONLY; no network-backed provider or feature activation. Source
permission and usable scoped evidence still block adapter, reconciliation and release.
Gate A/B UNVERIFIED; p1-catalog BLOCKED; Phase 05 DEFERRED. All 42 IDs preserved.
Phase 02 owner behavior accepted; visual QA deferred; real-game pilot after phase work.
One active writer. No merge/force-push. Read PROJECT_STATE, backlog, ADR 0006 and this
handoff before continuation. Publication receipts follow tested implementation commits.
