# AionCrafter — project state

2026-10-04 · Phase 03 groundwork merged; Phase 04 selected next · Brief v1.3 / ADR 0007.
Phase 03 IN_PROGRESS, real integration BLOCKED. Gates A/B UNVERIFIED. All 42 IDs retained.

## Verified merge and repository

Repository: https://github.com/T0rrag/AionCrafter
PR #5 https://github.com/T0rrag/AionCrafter/pull/5 is merged, under explicit user authorization.
Expected/tested head: 4e10fad95444241e68e353d41c9d24b4958b1dd6.
Merge commit on main: bd23f4166ffe276179843761dea8e95275efbce1; fetched complete tree matches that head exactly.
Documentation receipt follows the merge; always fetch actual heads before writing.
Receipt: delivery/phase-03-merge.json. Earlier Part 01/02 receipts preserve increment history.

User now authorizes tested phase merges and autonomous continuation (ADR 0007). Force-push,
concurrent overwrite, visibility/permission changes and bypassing required checks remain
unauthorized. Older PRs #1/#2/#3 were not merged or closed by this checkpoint.

## Delivered and remaining Phase 03

Freshness cache preserves observed/fetched/retrieval times separately, exact identity,
unknown ages, immutable replay and atomic validation. Request coordination includes
explicit batching, quota, bounded per-identity retries, Retry-After and shared cooldown.
Manual selections share immutable history with provider records without replacing the
provider cache. Quantity acquisition uses exact integer amounts and whole-stack/divisible
semantics, reports insufficient coverage, and labels reference-only estimates indicative.

p3-freshness/resilience/depth remain IN_PROGRESS: single-owner, in-memory contracts are
implemented, while production shared quota/cache ownership, transport timeout/cancellation,
application integration and market acceptance remain pending. p3-adapter/reconcile/releaseprice
BLOCKED on authorized source evidence. No automatic-price activation or live adapter.
See PHASE_03_GROUNDWORK.md. Gate A/B UNVERIFIED; Phase 05 DEFERRED; p1-catalog BLOCKED.

## Validation

Pre-merge Windows/Python 3.12.14: `python -m unittest discover -q` — 149 passed again.
54 Phase 03 tests include 60 small-book oracle cases and a combined persistence/fallback test.
Bootstrap checks passed (42 IDs / 83 checksums at merge candidate); diff check passed.
Prior compileall/catalog checks passed. GitHub returned no Actions runs, statuses, reviews
or comments for this candidate; no remote CI pass. The prior intermittent Windows HTTP
rejection-test reset remains documented, though the merge run passed.
Phase 02 owner behavior accepted; visual/keyboard QA deferred; game pilot after phase features.

## Next action and writer

Start Phase 04 — Crafting intelligence, Part 01, in a separate chat in the existing Aion2
project. First p4-batches: pure deterministic recursive expansion, shared-demand aggregation,
ceil by yield, leftovers and cycles; then integrate into manual workflows. Synthetic only.
Read handoffs/phase-03-to-phase-04.md and NEXT_CHAT_PROMPT.md. Do not restart Phase 03.

Existing phase/04-crafting-intelligence: 1bea9e9d687458eb78921fee31a979a568cbe3ae, historical
docs only. It is not an ancestor of current main because of one documentation commit.
Recheck and merge main into it normally, preserving both histories and current handoff;
no force-push. Open a new Phase 04 PR against main (old PR #4 was calculator code).
This Phase 03 chat stops application writes; next chat takes sole ownership when startup
is verified. Chat dispatch status is reported separately; preparing a handoff is not startup.
