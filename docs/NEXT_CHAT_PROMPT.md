Start AionCrafter Phase 03 — Market-price groundwork, Part 01, in this same Aion2 project.
Continue autonomously within this phase. The user selected Phase 03 preparation next;
ADR 0006 supersedes the next-Phase-04 instruction. Use a separate chat per phase.

First fetch https://github.com/T0rrag/AionCrafter and verify actual remote heads, ancestry
and PR state before writing. Read the latest docs/PROJECT_STATE.md, docs/backlog.json,
docs/handoffs/phase-02-to-phase-03.md, ADRs 0003–0006 and master prompt v1.3 sections
8/13/20/21. Retrieve current handoff documents from phase/02-manual-calculator if main
still has the older Phase 04 starter; do not follow that obsolete sequencing.

Last verified: main 81f6493999b6bca1e86cd621e7815f7d05944020 includes the calculator via
merged PR #4 (head 48dc8a304a9f917aec9caec27d62bd95041df530). Phase 02 acceptance
checkpoint 1bea9e9d687458eb78921fee31a979a568cbe3ae differs from main only in docs.
PR #3 remained open/draft. No Phase 04 features were implemented. Recheck these facts.
Create or resume phase/03-market-prices without overwriting work. Prefer verified main
as the base if it still contains the tested calculator; carry forward the latest handoff,
state and decisions from Phase 02. Record the actual base and any PR dependencies.

Scope: provider-independent groundwork using clearly labelled SYNTHETIC fixtures.
Inspect and reuse existing provider, observation, reference, persistence and UI contracts.

1. Begin p3-freshness: scoped cache behaviour preserving source-observed time separately
   from fetch/ingestion time. Cache hits or refreshes never make old prices new. Preserve
   unknown ages, zero versus unavailable, price type, rights and provenance. Use an
   injected clock and deterministic synthetic provider for tests.
2. Then p3-resilience: configurable batching, quotas, bounded retries/backoff, error/stale
   states and explicit manual fallback. Test without real network calls or sleeps;
   do not invent provider-specific limits or describe fixtures as a live integration.
3. Then p3-depth: exact quantity-aware acquisition for supported listing/stack inputs.
   Expose insufficient coverage; reference/minimum-only totals remain indicative with
   stock unverified. Do not assume partial-stack purchasing or listing depth support.

p3-adapter is BLOCKED until an authorized provider and working scoped sample exist.
Real p3-reconcile and p3-releaseprice remain BLOCKED on external evidence. Gate A stays
UNVERIFIED: synthetic tests do not pass it or enable automatic prices. Do not invent APIs,
credentials, licences or source rights. The restricted workbook is not an authorized
catalog. The user deferred real-game pilot validation until all phase feature work is
done; permission is still required before connecting a real source.

Baseline: 95 tests previously passed on Linux/Python 3.12.14. Rerun the fetched baseline,
add meaningful tests, then run python3 -m unittest discover -q, compileall, catalog
validation, git diff --check and scripts/validate_bootstrap.py as applicable. Preserve
all 42 IDs and refresh the manifest. Report actual commands, results and limitations.

Owner accepted Phase 02 behaviour and marked their review done. Visual/keyboard QA is
deferred and UNVERIFIED; do not restart cloud/Chromium troubleshooting. Phase 01 is
incomplete, p1-catalog BLOCKED, Phase 05 DEFERRED, Gate B UNVERIFIED. Historical craft/sale
fees and realized profit remain unknown without records. Recursive crafting/buy-versus-
craft belongs to Phase 04. Tax/fee/rounding inputs remain configurable.

Publish tested increments, verify remote SHAs and tree equality, open a draft Phase 03 PR
with its true base, and save state, handoff, tests and next prompt. Git shell push lacked
authentication previously; connected GitHub create_tree/create_commit/update_ref
(force:false) worked, followed by HTTPS fetch/tree verification. No merge or force-push.
This Phase 02 chat stops application writes; keep one active phase-branch writer.
Never claim new-chat startup, transcript synchronization or unexecuted tests as done.
