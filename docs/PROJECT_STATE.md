# AionCrafter — project state

2026-10-04 · Phase 03 / Part 01 · Brief v1.3; ADR 0006.
Phase 03 IN_PROGRESS. Gates A/B UNVERIFIED; automatic prices remain disabled.

## Repository and writer

T0rrag/AionCrafter · phase/03-market-prices · draft PR #5:
https://github.com/T0rrag/AionCrafter/pull/5 (base main).
This separate Aion2 Phase 03 chat is the active writer; no other writer was started.
Verified base main: 81f6493999b6bca1e86cd621e7815f7d05944020. Main contains the accepted
calculator through merged PR #4; its application tree matches Phase 02 handoff
cb0ce5cb9227184300055f1df8bb415b2ef2515e. Latest Phase 02 decisions/docs carried forward.
PR #3 remains draft/open but is not a dependency of PR #5. No Phase 04 implementation.
Freshness checkpoint 4d10338bf4e940f8929e062d8449d48e3499e340 was published, fetched and
verified equal to the tested tree 260bf1b58de02af779cfdf3b60334f98db5fdfd4.
Resilience/depth implementation f80b8e76c1542530b290f24e95088ab30707a4be is published and fetched; tested tree
b2cf609121113524c1e52a3a23809b87b90f3d49 matches exactly. Receipt:
`delivery/phase-03-part-01.json`. Documentation receipts follow implementation; fetch
the actual head before writing.

## Delivered groundwork

p3-freshness: scoped in-memory cache preserves original observed_at/fetched_at separately
from retrieval time and TTL. Unknown, stale, future, missing and zero remain distinct.
p3-resilience: explicit single/batch contract, caller-supplied quotas, bounded nonblocking
retry/backoff and Retry-After, shared cooldown, last-good error states and manual fallback.
p3-depth: exact quantity acquisition from coherent supplied listing snapshots, indivisible
stacks unless partial purchase is explicit, minimum cash cost, bounded exact search,
insufficient coverage and indicative/unverified-stock reference estimates.

All three tasks remain IN_PROGRESS: these are single-owner, provider-independent contracts
and tests, not production adapter/UI activation. See PHASE_03_GROUNDWORK.md for semantics,
limits and integration responsibilities. Existing manual calculator behavior is unchanged.
p3-adapter, p3-reconcile and p3-releaseprice remain BLOCKED on authorization, scoped samples,
source rights, usage limits and actual market reconciliation. Synthetic tests do not pass Gate A.

## Validation

Windows/Python 3.12.14: full suite 137 passed; Phase 03 targeted suite 42 passed.
Includes 60 deterministic small-book comparisons with an exhaustive oracle, and a combined
cache/outage/manual-fallback/depth/persistence scenario. Compileall and offline synthetic
catalog validation passed. Diff/bootstrap checks are recorded in TEST_RESULTS.md.
Baseline ran 95 tests with two pre-existing Windows SQLite migration-fixture cleanup errors;
explicit connection closing fixed those test fixtures without production storage changes.
One intermediate full run hit ConnectionResetError in an existing HTTP rejection test.
That test passed in isolation and the final full rerun passed; its intermittent Windows
transport behavior is not claimed fixed. No remote CI, browser or real-provider pass claimed.

## Boundaries and next action

All 42 IDs retained. Phase 01 incomplete/p1-catalog BLOCKED. Phase 02 owner behavior accepted;
visual/keyboard QA deferred and UNVERIFIED. Real-game pilot after phase feature work.
Phase 05 DEFERRED. No Chromium work, merge, force-push, release or deployment.
Part 01's authorized synthetic groundwork is implemented. Next Phase 03 continuation must
first inspect evidence for an authorized provider; without it, retain blocked integration
and review these contracts offline. Do not invent APIs, source rights, limits or game rules.
Stay on this branch/PR for Phase 03. Do not start Phase 04 in this chat. Read the handoff and
NEXT_CHAT_PROMPT; no new chat or transcript synchronization is claimed.
