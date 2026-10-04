# AionCrafter — project state

Checkpoint: 2026-10-04, Phase 01 / Part 03 (manual-first sequencing).
Brief: AionCrafter_Project_Prompt.md v1.3. Roadmap: v1.1 EN/ES, original HTML preserved.
Phase 01 status: **IN_PROGRESS**. Gate A: **UNVERIFIED**. Gate B: **UNVERIFIED**.

## Delivered and tested

The recovered architecture bootstrap is the actual baseline; the previously mentioned
application implementation was not present in the available artifacts and was not
assumed recovered. This checkpoint implements the data foundation in `aioncrafter/`.

| Task | Status | Scope/evidence |
|---|---|---|
| p1-identity | COMPLETE | Stable scoped item, variant, market and currency identity; tests/test_identity.py. |
| p1-catalog | BLOCKED | Pilot scope and permitted real catalog unresolved. 7 synthetic variants / 3 recipes only. |
| p1-recipe | COMPLETE | Inputs, batches, fees, requirements, joint/failure outcomes, unknown probabilities; models.py and model tests. |
| p1-trade | COMPLETE | Tradeability and acquisition restrictions/currencies; models.py and model tests. |
| p1-validate | COMPLETE | Strict import, duplicate/orphan/alias/cycle checks; catalog and storage tests. |
| p1-storage | COMPLETE | SQLite migrations, immutable records, rollback, concurrency and provider contracts; storage/CLI tests. |

Completion here means engineering implementation tested with synthetic fixtures,
subject to architectural review. It does not establish verified game rules or meet
p1-catalog's target of 100 real items and 25 verified recipes.
Phase 00 remains IN_PROGRESS (only inherited p0-audit complete). Phases 03 and 05 are
DEFERRED by user direction; Phases 02, 04 and 06 remain NOT_STARTED. Calculation records
are modeled, but an economics engine/UI is not built.

## Version and delivery

Repository: https://github.com/T0rrag/AionCrafter (public, as created by the user).
Default branch `main` was initialized from the verified empty repository at
`0ef1e2cae70eea6fa0b60f8c506e064433f9d440`.

Phase branch: `phase/01-data-foundation`.
Stacked base: `phase/00-architecture-bootstrap` at
`4e6077f51eb009bdfe8ffd5d5cf0328fcbef9481`.
Verified implementation upload: `703c7135539c69e639a5d75334ece19d55a8afe9`.
Its tree exactly matches tested local checkpoint `c559adeaa2ed060239656ff7cff1a504da8700f5`.
Later commits on this branch record delivery documentation; fetch the current head
before editing. See `delivery/2026-10-04-phase01.json` and GITHUB_DELIVERY.md.

Architecture PR: https://github.com/T0rrag/AionCrafter/pull/1 — open for review.
Phase PR: https://github.com/T0rrag/AionCrafter/pull/2 — draft, based on PR #1's branch.
The earlier 404/access blocker is resolved. Both remote trees and branch SHAs were
read back and verified. No merge, release, deployment or visibility change performed.

## Evidence and next action

47 local tests passed: `python3 -m unittest discover -v`.
Offline fixture validation passed. See TEST_RESULTS.md for limits and individual suites.
All 42 backlog IDs retained; roadmap progress is in `roadmap-progress.json`, imported
through the existing bilingual roadmap control without modifying its code or storage key.

Next eligible chat: Phase 02 — Manual-first calculator, Part 01. The user directed
continued development with automatic live prices and overlay deferred (ADR 0003).
Start p2-economics on the tested engineering contracts using labeled synthetic data;
then integrate manual price entry and both requested workflows. p1-catalog remains
BLOCKED and Phase 01 is not declared complete. Its real-data requirement is retained.

Phase 02 implementation belongs in a new chat. Verify and record the actual base for
phase/02-manual-calculator; stack its PR on phase/01-data-foundation if PR #2 remains
unmerged. No merge is authorized. Gate A/B remain UNVERIFIED; Phases 03/05 are DEFERRED.

Latest handoff: `handoffs/phase-01-part-03.md`. Starter: `NEXT_CHAT_PROMPT.md`.
Earlier handoffs are historical records and remain preserved.
