Continue AionCrafter Phase 02 — Manual-first calculator, Part 02, in this same project.
Use master prompt v1.3 sections 8, 13, 20 and 21 plus ADR 0003. Read docs/PROJECT_STATE.md,
docs/handoffs/phase-02-part-01.md and docs/backlog.json first.

Fetch T0rrag/AionCrafter, verify actual phase/02-manual-calculator head and draft PR #3.
Its tested implementation is 7afffae4ca62e0c049429665b93ade5d25948175 (62 tests);
delivery docs follow it. Base is 3a395eb5894e65ff0d67e336d1a91dc452136843 on
phase/01-data-foundation; PR #3 is stacked on unmerged PR #2. Reuse branch/PR;
no merge or force-push.

Begin p2-costmodes: separate replacement cost, additional cash after owned inventory,
and historical cost only with supplied records. Then p2-save: persist manual
observations/plans/settings and validated import/export/reset. Finish product search,
editor provenance acceptance and browser QA; previous visual check was blocked by
unavailable browser admin-policy verification. Keep exact arithmetic and missing-price
states. Use SYNTHETIC fixtures; p1-catalog BLOCKED and Phase 01 incomplete. Phases 03/05
DEFERRED, Gates A/B UNVERIFIED. Work only within Phase 02, test coherent increments,
publish checkpoints, verify remote SHAs, save state and a handoff.
