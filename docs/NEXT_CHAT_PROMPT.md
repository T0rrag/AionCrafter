Start AionCrafter Phase 04 — Crafting intelligence, Part 01 in the existing Aion2 project.
Continue autonomously. Fetch https://github.com/T0rrag/AionCrafter and verify actual heads.
PR #5 is merged at bd23f4166ffe276179843761dea8e95275efbce1; documentation receipt follows on main.
Read AGENTS.md, docs/PROJECT_STATE.md, handoffs/phase-03-to-phase-04.md, ADR 0007,
backlog.json and master brief v1.3 sections 8/13/20/21.

Resume phase/04-crafting-intelligence after checking its historical 1bea9e9d687458eb78921fee31a979a568cbe3ae
head. Merge current main into it without force, preserve both histories/current handoff,
and open a new Phase 04 PR (old PR #4 is closed and contained calculator code).
First p4-batches: pure deterministic recursive expansion, aggregate shared demand before
rounding by yields, carry leftovers and detect cycles. Then independent Phase 04 work.
Use SYNTHETIC fixtures/manual references and exact arithmetic. Baseline: 149 tests passed.

The user now authorizes tested phase merges (ADR 0007); no force-push, concurrent overwrite
or bypass of required checks. Preserve all 42 IDs. Phase 03 stays incomplete with real
integration blocked; Gates A/B UNVERIFIED, p1-catalog BLOCKED, Phase 05 DEFERRED.
No real-provider activation or guessed game rules. Visual QA deferred; no Chromium work;
game pilot after phase features. One active writer; publish and verify tested increments.
