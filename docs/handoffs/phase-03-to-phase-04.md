# Phase 03 to Phase 04 — merged-groundwork handoff

2026-10-04. Brief v1.3; ADR 0007. Phase 03 IN_PROGRESS, not complete. Independent groundwork
merged; real-provider integration stays BLOCKED. Next eligible phase: 04, p4-batches.

## Verified delivery

PR #5 https://github.com/T0rrag/AionCrafter/pull/5 merged after the user explicitly allowed
merges and autonomous continuation. Tested head 4e10fad95444241e68e353d41c9d24b4958b1dd6;
merge commit bd23f4166ffe276179843761dea8e95275efbce1. Read-back confirms merged=true. HTTPS fetch and
git diff --exit-code confirm its full tree equals the tested head. Documentation receipt
follows; fetch actual main. No force-push or unrelated historical PR merge/closure.

Pre-merge `python -m unittest discover -q`: 149 passed on Windows/Python 3.12.14. Bootstrap
and diff checks passed; all 42 task IDs retained. GitHub Actions/status/review/comment
queries returned empty lists, not a remote CI pass. Prior intermittent Windows HTTP
rejection-test reset is documented; this run passed. Full code semantics/tests are in
PHASE_03_GROUNDWORK and Part 01/02 handoffs. All fixtures remain SYNTHETIC ONLY.

Phase 03 delivered identity-scoped age-preserving cache; configurable nonblocking quotas,
per-identity retries/backoff and manual fallback; exact whole-stack/divisible acquisition.
Manual/provider IDs share immutable history; invalid batches reserve nothing. Production
shared quota/cache ownership, transport and application integration remain pending.
No real adapter or automatic-price feature activation. Gate A/B remain UNVERIFIED;
p3-adapter/reconcile/releaseprice and p1-catalog BLOCKED; Phase 05 DEFERRED. Phase 02
behavior accepted; visual QA deferred; real-game pilot after phase features. No Chromium work.

## Phase 04 start

Use a new chat in the existing Aion2 project. First inspect AGENTS, PROJECT_STATE,
backlog, ADR 0007, this handoff, master brief sections 8/13/20/21, existing economics,
valuation, identity and catalog contracts. Keep Phase 04 application writes out of this chat.

Existing remote phase/04-crafting-intelligence at 1bea9e9d687458eb78921fee31a979a568cbe3ae
has no Phase 04 features; one historical docs commit is outside main's ancestry. Recheck
all heads before edits, then merge current main into that branch normally, resolving old
docs to the current handoff without discarding history. No force-reset or force-push.
Old PR #4 is merged/closed and represented calculator work; open a new Phase 04 PR to main.

Implement p4-batches first: deterministic recursive yields, aggregate shared materials
before rounding, carry leftovers, reject cycles/unknown stochastic outcomes. Use exact
money and explicit missing prices. Extend p4-buycraft and other independent Phase 04 tasks
only with evidence-backed semantics; do not invent probabilities, fees, source rights or
market liquidity. Preserve all 42 IDs and incomplete statuses. Test pure functions before
application integration, publish coherent checkpoints, verify remote tree/SHA, maintain
handoff/starter. User-authorized tested phase merges are now allowed; required checks and
external source gates still apply. One writer; this Phase 03 chat stops after handoff.
