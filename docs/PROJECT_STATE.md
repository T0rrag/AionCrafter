# AionCrafter — project state

Checkpoint: 2026-10-04, Phase 02 / Part 02. Brief v1.3 plus ADR 0003.
Active Phase 02: **IN_PROGRESS**. Phase 01: **IN_PROGRESS**; p1-catalog: **BLOCKED**.
Phases 03/05: **DEFERRED**. Gates A/B: **UNVERIFIED**.

## Verified repository and dependency

Repository: https://github.com/T0rrag/AionCrafter
Branch: `phase/02-manual-calculator`.
Recorded base: `phase/01-data-foundation` at `3a395eb5894e65ff0d67e336d1a91dc452136843`.
PR #2 was open, draft and unmerged when verified. Phase 02 draft PR #3 is explicitly
stacked on that branch: https://github.com/T0rrag/AionCrafter/pull/3.
No merge, force-push, release or deployment performed.

Published economics checkpoint: `2c614636f9ef22d799732d20455aa2cb4f25610d` (55 tests).
Published Part 01 workflow: `7afffae4ca62e0c049429665b93ade5d25948175` (62 tests).
Published Part 02 implementation: `4594c5a6c825733bd49c56c14cddfd41a3161ab7` (77 tests).
Published implementation commits were fetched and their trees matched tested local checkpoints
exactly. Delivery documentation follows the implementation SHA; fetch the actual head
before editing. Shell Git push lacked usable authentication; connector commits and
non-force ref updates published the same tested trees. See delivery receipt.

## Delivered increments and remaining scope

| Task | Status | Evidence / remaining work |
|---|---|---|
| p2-economics | IN_PROGRESS | economics.py: exact integer currency units, rational ROI/break-even, deterministic batches, configurable tax/fixed fees/proceeds rounding, minimal break-even currency tick, missing/unknown states. 9 new economics tests. Needs owner review and broader joint-output/market fee-rule acceptance. |
| p2-editor | IN_PROGRESS | manual.py/web.py: explicit market/currency/faction and timezone-aware observation time; blank prices unavailable. Manual observations persist with original timestamps and linked overrides in saved plan revisions. Approved vendor/snapshot reference imports and age presentation remain. |
| p2-listflow | IN_PROGRESS | Selected quantities or quantity-TAB-alias paste; variant picker for ambiguous names; unit/subtotal/known subtotal/incomplete total. Browser visual/pilot QA remains. |
| p2-itemflow | IN_PROGRESS | Product/recipe selection, direct ingredients, deterministic batch yield and leftovers, manual selling price and margin. English/Spanish alias product search added. Direct ingredients supported; browser QA and remaining acceptance remain; recursive optimization stays Phase 04. |
| p2-costmodes | IN_PROGRESS | valuation.py and 6 tests: inventory-adjusted shopping/cash, unchanged replacement value, recorded allocated material cost with explicit missing records. Historical crafting/sale fees and realized profit are not inferred. |
| p2-save | IN_PROGRESS | plans.py/web.py and 7 plan tests: SQLite revisions, favorites/settings/prices/inventory/history, validated JSON/CSV transfer, reset/deletion, timestamp preservation and stale-writer checks. Browser/pilot acceptance remains. |

Inputs are the unchanged **SYNTHETIC ONLY** catalog (7 variants, 3 recipes). Unknown
probabilities are refused for deterministic economics; no expected-outcome engine is
claimed. Leftovers and coproducts earn no credited revenue; all batch costs are charged
to planned sales. Craft-fee per-output-unit counts all produced output units. Per-batch
and per-attempt each count one recipe invocation. Tax rounding is a user-selected
assumption applied once to batch proceeds; no verified game tax or rounding rule exists.
Stock, sell-through and craft requirements remain unverified/manual checks.

## Validation and limits

Baseline: 47 tests passed on Python 3.14.7. Economics checkpoint: 55 tests passed.
Current: `python3 -m unittest discover -q` — 77 tests passed. A strengthened import/save
provenance assertion then passed all 7 targeted plan tests. Coverage includes local HTTP GET,
POST, foreign-Origin refusal and oversized-body refusal. Loopback tests require an
unsandboxed execution permission in this environment. Offline catalog validation and
compileall passed. Bootstrap manifest/task validation passed; see TEST_RESULTS.md.
Inherited SQLite ResourceWarnings on Python 3.14 remain; no new SQLite code was changed.
Browser visual verification could not run: browser admin-policy verification was
unavailable and access was denied. No browser/pilot/game/live-provider/overlay/remote-CI
success is claimed. Phase 00 remains IN_PROGRESS; p1 engineering retains its existing
evidence and p1-catalog still requires a permitted pilot catalog, 100 real items and 25
verified recipes.

Next: continue Phase 02 Part 03 on this branch/PR: finish source-aware reference imports,
price age display and acceptance tests/browser QA. Read `handoffs/phase-02-part-02.md`.
The attempt to create a local continuation in Aion2 was rejected because it is a ChatGPT
project requiring cloud Work. Cloud-execution clarification is pending; no new chat
was created. Work continued locally for this checkpoint.

Autonomous continuation is now authorized by the user (ADR 0004). Create same-project
continuation chats at phase boundaries or when context grows large, carrying the
checkpoint and constraints. Context recovery confirmed prior architecture and Phase 01
decisions; related translation work provides no permitted catalog.
