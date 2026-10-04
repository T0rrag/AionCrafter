# ADR 0004 — Autonomous continuation and phase-scoped chats

Date: 2026-10-04. Status: user-directed workflow update.

The user explicitly authorized continued autonomous development and creation of new
chats inside the existing Aion2 project whenever context becomes too large and whenever
work reaches a new phase. This supersedes the earlier default that the user must open
the next chat manually. It does not change the seven phases or 42 task IDs.

Before handing off, persist tested code, actual validation, current state, remaining
work and the next starter; publish coherent authorized checkpoints and verify remote
SHAs. Create the continuation chat with those precise references, confirm that it
started, and avoid simultaneous writers on the same phase branch. Use a new Part within
the same phase when context grows; use a new phase chat at a genuine phase boundary.
A larger history is a reason to hand off, not evidence that a phase is complete.

Continue independent engineering without asking routine permission. Genuine missing
external permissions/data and unverified acceptance criteria remain blockers to those
specific activities; do not invent completion. Preserve prior constraints: no merge
or force-push; p1-catalog BLOCKED and Phase 01 IN_PROGRESS; Phases 03/05 DEFERRED and
Gates A/B UNVERIFIED. New chats carry this authorization and the current phase scope.

If the app cannot create a chat in this project, record the actual tool limitation,
continue eligible work in the available chat, and do not claim a chat was created.

## Context reconciled for the continuation

The architecture chat, Phase 01 chat and its implementation executor, current Phase 02
chat, repository records and PR #3 were recovered. Related AION2 translation chats
were inspected for catalog evidence: a workbook was viewable, but copying, downloading
and printing were restricted and a Drive fetch returned 403. That is not a permitted
catalog for this application. No real data from it is imported. No matching AionCrafter
Page was found; the local project sources directory contains no synced reference files.
Archived-chat listings were empty. No unavailable historical source is assumed read.

Latest verified Phase 02 head before this workflow update:
293e46083a1ef5d9d4c29190a87ab681a1fa2bb9. PR #3 remains draft/unmerged and stacked on
Phase 01. Continue from docs/handoffs/phase-02-part-01.md. No new application tests
are claimed for this documentation-only workflow update.
