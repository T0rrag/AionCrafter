# Phase 04 Part 02 handoff

2026-10-04 · Brief v1.3 / ADR 0007 / ADR 0008. Phase 04 IN_PROGRESS.
Gates A/B UNVERIFIED. All 42 backlog IDs preserved; one active Phase 04 writer.

## Repository and delivery

Repository: https://github.com/T0rrag/AionCrafter
Branch: phase/04-crafting-intelligence. PR #6: https://github.com/T0rrag/AionCrafter/pull/6.
Verified Part 01 receipt head: 88071d4cbd65df2f066310441c3231aea2173a04.
Main before Part 02: 4f06404f1846f4d586dbbf71ae7e90b5a897435f.
Part 02 candidate is ready for publication and remote checks; no merge is claimed here.
Its delivery receipt follows the verified upload. Fetch actual heads before writing.
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
passed; `git diff --check` passed. Bootstrap validation runs after manifest refresh.
Fixtures/evidence are SYNTHETIC only. No remote CI pass, visual QA or game pilot claim.

## Boundary and remaining evidence

After verified PR #6 merge/receipt, next eligible independent work is Phase 06 manual
release preparation in a separate Aion2 chat (ADR 0008). No Phase 06 application work
starts here. Phase 04 remains incomplete for real-market integration. Phase 03 stays
IN_PROGRESS with real adapter/reconciliation/activation BLOCKED; production quota/cache/
transport integration pending. p1-catalog BLOCKED; Phase 05 DEFERRED; Gates A/B UNVERIFIED.
Visual/keyboard QA remains deferred by the owner; no Chromium troubleshooting. Real-game
pilot follows phase features. No public release until applicable quality evidence exists.

## Contracts to preserve

stochastic.py binds exact recipe/bonus content in AttemptEvidence. Unknown probability,
consumption or independence evidence keeps expected values unknown. Never turn these
expectations into deterministic recursive yields. ranking.py recomputes source age and
uses replacement cost for profit/ROI and additional cash for budget; exclusions remain
visible. ledger.py uses actual receipts only, explicit FIFO and exact fractional basis.
Ledger storage is separate from plans and requires immutable prefix/expected revision.
The form at /ledger previews records before save and preserves a valid preview on errors.

Manual probability/eligibility attestations are not app-verified game evidence. Model
extensions (conditional bonuses, repeat-attempt risk, reversal events, general route
optimization) require separately specified semantics, not guesses or silent fallbacks.
Current visual QA is deferred, not passed. Keep the 42 stable IDs and historical handoffs.
