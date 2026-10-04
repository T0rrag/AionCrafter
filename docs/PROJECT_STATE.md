# AionCrafter — Phase 04 manual groundwork

2026-10-04 · Brief v1.3 / ADR 0007 / ADR 0008. Phase 04 IN_PROGRESS.
Gates A/B UNVERIFIED. All 42 backlog IDs preserved; one active Phase 04 writer.

## Repository and delivery

Repository: https://github.com/T0rrag/AionCrafter
Merged branch: phase/04-crafting-intelligence. PR #6: https://github.com/T0rrag/AionCrafter/pull/6.
Verified Part 01 receipt head: 88071d4cbd65df2f066310441c3231aea2173a04.
Main before Part 02: 4f06404f1846f4d586dbbf71ae7e90b5a897435f.
PR #6 is merged. Tested head: e34ddf478c63777a0e0555664337d7eed2900134.
Merge on main: a185d0618cb315aa9468aec0de7716ccb1d56146.
Read-back merged=true; fetched merge tree exactly matches the tested candidate.
Receipt: delivery/phase-04-merge.json. Documentation receipt follows; fetch actual heads.
User authorizes tested merges; no force-push, concurrent overwrite or check bypass.

## Independent engineering delivered

Part 01: iterative deterministic recursive batches, shared-demand rounding, owned stock,
coproducts/leftovers and bounded quantity-aware buy/craft comparisons; local saved plans.
Part 02: one-attempt expected/downside scenarios with explicit probability/consumption
evidence and separate independent-bonus contracts; source stock/volume distinctions;
conditional rankings with explicit budget/profession/requirements/vendor/age filters;
actual FIFO purchases/crafts/sales, unknown basis, exact allocations, failed-craft expense,
estimate comparison, immutable SQLite revisions, local forms and lossless JSON transfer.

p4-batches and p4-ledger COMPLETE for the independent engineering scope. p4-buycraft,
p4-proc, p4-liquidity and p4-rank IN_PROGRESS pending validated real rule/catalog/market
integration and acceptance. No global route optimum, repeat-attempt risk model, source
verification or automatic provider activation is claimed. See PHASE_04_CRAFTING.md,
PHASE_04_SCENARIOS_AND_LEDGER.md and handoffs/phase-04-part-02.md.

## Executed validation

Windows / Python 3.12.14: `python -m unittest discover -q` — 238 passed (21.480s).
58 Part 02 tests: 14 stochastic, 8 liquidity, 14 ranking, 15 ledger, 7 HTTP form;
ledger includes 60 conservation cases. Compilation and synthetic catalog validation
passed; `git diff --check` passed. Pre-merge bootstrap validation passed: 42 IDs and 109 checksums.
GitHub returned no reviews/comments/statuses/PR workflow runs; this is not a CI pass.
Fixtures/evidence are SYNTHETIC only. No remote CI pass, visual QA or game pilot claim.

## Boundary and remaining evidence

PR #6 merge/receipt is verified. Next eligible independent work is Phase 06 manual
release preparation in a separate Aion2 chat (ADR 0008). No Phase 06 application work
starts here. Phase 04 remains incomplete for real-market integration. Phase 03 stays
IN_PROGRESS with real adapter/reconciliation/activation BLOCKED; production quota/cache/
transport integration pending. p1-catalog BLOCKED; Phase 05 DEFERRED; Gates A/B UNVERIFIED.
Visual/keyboard QA remains deferred by the owner; no Chromium troubleshooting. Real-game
pilot follows phase features. No public release until applicable quality evidence exists.

Phase 04 application writes stop at this handoff. No Phase 06 chat has been created or
started by this checkpoint. Remote phase/06-release was absent at receipt time; recheck
and create from current reviewed main if still absent. See handoffs/phase-04-to-phase-06.md.
