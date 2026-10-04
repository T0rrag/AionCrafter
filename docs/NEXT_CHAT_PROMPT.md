Continue AionCrafter in this same project: Phase 01 — Data foundation, Part 03.
Read docs/PROJECT_STATE.md, docs/handoffs/phase-01-part-02.md, docs/backlog.json and
ADR 0002. Follow AionCrafter_Project_Prompt.md v1.3 sections 9, 13, 20 and 21.

Repository: https://github.com/T0rrag/AionCrafter. Fetch and verify the current head
of phase/01-data-foundation. PR #2 is draft and stacked on documentation PR #1
(phase/00-architecture-bootstrap). Both are unmerged. Verified implementation commit:
703c7135539c69e639a5d75334ece19d55a8afe9; later commits record delivery documentation.

47 local tests passed. First review the current foundation and resolve p1-catalog:
select a real pilot region/server-or-market/faction/build/language and obtain a
permitted, verified catalog (target 100 relevant items / 25 verified recipes).
Current fixtures are only 7 SYNTHETIC variants / 3 SYNTHETIC recipes. Do not count
synthetic expansion as completion of the real-data task or infer reuse permission.

Continue Phase 01 only. Keep Gate A and Gate B UNVERIFIED without new evidence.
Do not build Phase 02 UI, force-push or merge without architectural/owner approval.
Record tests, commit/upload coherent checkpoints, verify remote SHAs and update the
existing PR, state and handoff before stopping.
