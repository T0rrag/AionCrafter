# Phase 04 Part 01 handoff

2026-10-04 · Brief v1.3 / ADR 0007. Phase 04 IN_PROGRESS, one active writer in its
separate Aion2 chat. All 42 backlog IDs retained. Gates A/B UNVERIFIED.

## Baseline and delivery

Repository: https://github.com/T0rrag/AionCrafter
Phase 03 PR #5 merged at bd23f4166ffe276179843761dea8e95275efbce1; main documentation
receipt 4f06404f1846f4d586dbbf71ae7e90b5a897435f. The existing Phase 04 branch was
normally merged with main, preserving both histories, at
3a1e9bab7e3f6e747cfe4beb3a40bd68724e9859. Its tree matched main before feature work.
Current branch: phase/04-crafting-intelligence. This checkpoint prepares its new draft
PR against main; old PR #4 is closed. Read the delivery receipt and actual remote heads.
User authorizes tested merges; no force-push, concurrent overwrite or bypass of checks.

## Delivered in this increment

Pure deterministic recursive batches aggregate shared demand before rounding, support
joint outputs and owned stock, retain leftovers, reject cycles/unknown outcomes and
use an iterative dependency walk. Quantity-aware route costs include every executed
recipe's fees and exact external acquisition. Two explicit objectives: additional
cash after stock and replacement cost without stock deduction.

The local calculator has a crafting workflow, selected recipe expansion and bounded
whole craft-or-buy comparisons, with saved-plan round trips and source/age labels.
Missing prices/fees stay unknown; inventory has no double use; leftovers have no resale
credit. The search does not include mixed buy/craft of one variant or simultaneous
competing producers and is not a general optimizer. Requirements remain manual checks.
See PHASE_04_CRAFTING.md and handoffs/phase-04-part-01.md.

## Validation and limits

Windows / Python 3.12.14: `python -m unittest discover -q` — 180 tests passed,
including 15 batches, 13 route-cost tests and 3 additional HTTP form acceptance tests.
The HTTP tests are not visual QA. Visual/keyboard QA remains deferred; no Chromium work.
All fixtures are SYNTHETIC. Real-game pilot follows phase feature development.

p4-batches and p4-buycraft remain IN_PROGRESS: deterministic groundwork delivered;
stochastic treatment, requirements/vendor eligibility and broader acceptance remain.
p4-proc/liquidity/rank/ledger not started. Next implement verified-input stochastic
scenario contracts and downside/expected values, preserving unknown probabilities.
Phase 03 remains IN_PROGRESS with real adapter/reconciliation/activation BLOCKED;
production quota/cache/transport integration remains pending. p1-catalog BLOCKED;
Phase 05 DEFERRED. No live provider or automatic-price activation.

## Continuation details

Resume the same branch and phase PR after fetching actual heads. Do not repeat the
baseline merge, restart Phase 03 or open a new phase branch. This chat is sole writer.
Read batches.py, buycraft.py, crafting_view.py and their synthetic tests. Explicit
limits: library callers supply route/search budgets; UI allows at most seven candidates
(128 subsets) and displays up to twenty route summaries. A deterministic selected plan
rejects ambiguous producers. Currency amounts use integer minor units throughout.
The target recipe fee override applies only to that recipe. Historical cost fields
are retained but are not applied to recursive cash/replacement estimates.

Next tasks: p4-proc, then p4-liquidity/rank and optional ledger, with pure functions
and synthetic verification before UI integration. Never turn an expected stochastic
yield into a guaranteed craft count, or a listed asking price into completed-sale
evidence. Preserve external blockers and do not mark this partial phase complete.
