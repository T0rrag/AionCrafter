# AionCrafter working instructions

Read docs/PROJECT_STATE.md, the latest handoff, docs/backlog.json and current ADRs first.
The authoritative brief is AionCrafter_Project_Prompt.md v1.3 (workflow sections 20–21).
Preserve all seven phases and 42 stable IDs with evidence-backed statuses.

Current sequence: Phase 04 manual groundwork merged via PR #6; read PROJECT_STATE,
handoffs/phase-04-to-phase-06.md and ADR 0008. p4-batches/ledger engineering complete;
Phase 04 remains IN_PROGRESS for real rules/catalog/market integration. Read verified merge
receipt before moving to independent Phase 06 manual-release preparation in a separate
Aion2 chat. Phase 03 remains IN_PROGRESS with real integration BLOCKED; p1-catalog
BLOCKED; Phase 05 DEFERRED; Gates A/B UNVERIFIED. Do not claim a release or real pilot.

Use exact money; missing prices are not zero. Preserve observation source/time, market,
build and variant identity. Synthetic fixtures must remain clearly labelled. Do not invent
source rights, APIs, quotas, game fees or probabilities. Source permission is required
before real connection; full gate evidence precedes automatic-price activation.

The user authorizes autonomous development and tested phase merges (ADR 0007 supersedes
historical no-merge wording). Never force-push, overwrite concurrent work, bypass required
checks or change visibility/permissions. No bulk merge of historical PRs is implied.
Verify remote heads and PR state before writes/merges, use expected-head checks, run
applicable tests, and read back actual SHAs/tree equality. An upload/merge is not phase
completion, real-market acceptance, release or deployment.

Use one phase branch/PR and one active writer. Create a separate chat in existing Aion2
for each new phase or context handoff; save and verify continuity first, verify startup,
then stop writes in the previous chat. Do not claim chat creation or transcript sync
without evidence. Preserve incomplete work and external blockers in every handoff.

At checkpoints update PROJECT_STATE, backlog evidence, test results, manifest, handoff
and NEXT_CHAT_PROMPT; publish coherent increments and verify the remote SHA. Phase 02
behavior is accepted, visual/keyboard QA deferred, real-game pilot after phase feature
work. Do not restart Chromium/cloud-browser troubleshooting.
