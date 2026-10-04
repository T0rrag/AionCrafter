# AionCrafter — Phase 02 / Part 01 handoff

Date: 2026-10-04. Brief: v1.3 sections 8, 13, 20–21 plus ADR 0003.
Phase 02: IN_PROGRESS. Repository: https://github.com/T0rrag/AionCrafter
Branch: phase/02-manual-calculator. Draft PR: https://github.com/T0rrag/AionCrafter/pull/3.

## Delivered and verified

Read Phase 01 state/handoff/backlog first; fetched actual Phase 01 branch at
3a395eb5894e65ff0d67e336d1a91dc452136843 and verified PR #2 remains unmerged.
Created Phase 02 from that exact base and explicitly stacked PR #3 on PR #2.
Baseline passed 47 tests. Two tested checkpoints were published:

- 2c614636f9ef22d799732d20455aa2cb4f25610d: pure deterministic economics, 55 tests.
- 7afffae4ca62e0c049429665b93ade5d25948175: manual web workflows, 62 tests.

Fetched both uploads and verified identical trees against tested local checkpoints.
Git shell authentication failed; connected GitHub tree/commit/ref tools published
without force. Local duplicate commits were skipped by a normal rebase onto the
verified remote equivalents. No remote history rewrite occurred.

p2-economics uses integer minor currency units; ROI and unrounded break-even are exact
rational values. Configurable tax, fixed sale fees and explicit proceeds rounding;
fee basis distinguishes output units from craft invocations. Binary search finds the
smallest currency tick that covers rounded proceeds. Missing material/sale prices,
unknown crafting fees, zero-cost ROI and full-tax break-even stay explicit.

p2-editor requires explicit market, currency and timezone-aware observed time; blank
prices remain unavailable. p2-listflow accepts selected quantities or pasted
quantity-TAB-exact-alias rows, with an ambiguity picker. p2-itemflow selects a product
and recipe and shows direct ingredients, batch quantities, leftovers and margin.
All four tasks remain IN_PROGRESS pending their remaining acceptance work.

## Tests actually run

`python3 -m unittest discover -q`: baseline 47, economics 55, final 62 passed.
`python3 -m compileall -q aioncrafter`: passed.
`python3 -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json`: passed.
`python3 scripts/validate_bootstrap.py`: passed after manifest refresh.
HTTP tests cover GET/POST and Origin/body-size refusal. Initial tests caught an
incorrect ambiguity-test fixture and sandbox socket restriction; corrected to the
actual ambiguous potion alias and reran with loopback permission. Python 3.14 emits
inherited SQLite ResourceWarnings. Browser verification failed because admin-policy
verification was unavailable; no visual QA is claimed. Remote CI/pilot/game tests
were not run.

## Decisions and constraints

SYNTHETIC fixtures only; no game fees, probabilities or catalog rights invented.
Unknown/non-deterministic outcomes are rejected, not guessed. Direct ingredients only.
All batch costs are charged to planned sales; leftovers/coproducts receive no revenue.
Craft requirements and stock are manual/unverified. Fees/rounding are explicit user
assumptions. No persistence yet; form resubmission keeps inputs but closing loses them.

## Remaining work and next session

p2-costmodes and p2-save NOT_STARTED. Add inventory/additional cash/replacement cost
and supplied historical-cost data, then persist observations/plans with validated
import/export/reset. Finish product search, review editor/reference distinctions,
expanded-tree scope and browser QA within Phase 02; do not begin Phase 04 optimization.
Phase 01 remains IN_PROGRESS and p1-catalog BLOCKED. Phases 03/05 DEFERRED, Gates A/B
UNVERIFIED. No merge or force-push authorized. Continue Part 02 on this same PR.
Read PROJECT_STATE.md, backlog.json, this handoff, ADR 0003, brief sections 8/13/20/21,
and economics.py/manual.py/web.py plus their tests. Fetch actual branch head first.
