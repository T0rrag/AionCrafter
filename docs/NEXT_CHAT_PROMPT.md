Start AionCrafter Phase 02 — Manual-first calculator, Part 01, in this same project.
Use master prompt v1.3 sections 8, 13, 20 and 21 plus ADR 0003. Read PROJECT_STATE.md,
handoffs/phase-01-part-03.md and backlog.json first.

Fetch https://github.com/T0rrag/AionCrafter and verify the actual phase/01-data-foundation
head. Its implementation passed 47 tests. Create phase/02-manual-calculator with a
recorded base SHA; if PR #2 remains unmerged, explicitly stack the Phase 02 PR on it.
Do not merge or force-push.

Begin p2-economics: pure exact-arithmetic batch costs, configurable fees, proceeds,
profit/loss, ROI, break-even and explicit missing-price states. Then add manual price
entry and both materials-only and item-economics workflows in coherent increments.

The user postponed live prices and overlay: Phases 03/05 are DEFERRED, Gates A/B
UNVERIFIED. p1-catalog remains BLOCKED; Phase 01 is not fully complete. Use clearly
SYNTHETIC fixtures while real pilot/catalog permissions are unresolved. Do not invent
verified game data, fees or probabilities. Work only on Phase 02, run relevant tests,
publish tested checkpoints, verify remote SHAs, and save state and a handoff.
