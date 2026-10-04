Start AionCrafter Phase 04 — Crafting intelligence, Part 01 inside this same Aion2 project.
Follow master prompt v1.3 and ADRs 0003/0004/0005. The user directs normal feature
development and a new chat for each phase; do not spend this phase on Chromium/cloud QA.

Fetch T0rrag/AionCrafter, inspect phase/04-crafting-intelligence if present, and verify
its actual head/base before editing. Otherwise create it from the current verified
phase/02-manual-calculator handoff. Read docs/PROJECT_STATE.md, docs/backlog.json and
docs/handoffs/phase-02-to-phase-04.md. Phase 02 PR #3 is unmerged; explicitly stack the
new phase branch/PR on it. The Phase 02 code baseline passed 95 tests.

First implement p4-batches: pure deterministic recursive recipe expansion, shared-demand
aggregation before batch rounding, explicit recipe selection and leftover accounting.
Use labeled synthetic fixtures and test boundaries, shared intermediates and rejection
of cycles/unsupported stochastic outcomes. Keep exact arithmetic and scoped identity.

Visual/pilot acceptance is tracked for later; it does not block this engineering phase.
The user schedules the real-game pilot after all phase feature work and marked PR
review done in chat (no GitHub closure/merge). Owner behaviour acceptance is complete;
presentation/controls customization scope is unspecified. Read the ADR 0005 addendum.
Phase 01/catalog incomplete; Phases 03/05 DEFERRED; Gates A/B UNVERIFIED. Preserve all
42 IDs. Upload tested increments, verify SHAs, open a draft Phase 04 PR, and save state
and handoff. No merge/force-push. Previous chat stops application writes at handoff.
