# AionCrafter working instructions

Read docs/PROJECT_STATE.md, the latest handoff, docs/backlog.json and current ADRs first.
The authoritative brief is AionCrafter_Project_Prompt.md v1.3 (workflow sections 20–21).
Preserve all seven phases and 42 stable IDs with evidence-backed statuses.

Current sequence: Phase 06 manual-edition validation/recovery, Part 01, on
phase/06-release. Read PROJECT_STATE, handoffs/phase-06-part-01.md, the latest
NEXT_CHAT_PROMPT/immutable continuation, delivery/phase-06-part-01.json and ADR 0010.
p6-mathqa regression requirement COMPLETE; p6-patches/security/package IN_PROGRESS;
p6-usertest/golive BLOCKED on applicable evidence. Continue Part 02 within Phase 06.
Phase 04 manual groundwork is merged but real integration incomplete; Phase 03 real
integration/p1-catalog BLOCKED; Phase 05 DEFERRED; Gates A/B UNVERIFIED. No release.

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

## Mandatory end-of-chat GitHub continuation

GitHub is the canonical cross-device recovery record for development sessions. Do not rely
on ChatGPT/Work conversation sync as the only copy of phase context.

Before any development chat is considered finished:

1. Fetch and verify the actual remote branch/PR/main heads before final writes.
2. Run the applicable tests, validators and diff checks for the work being handed off.
3. Publish the coherent tested checkpoint to the active phase branch/PR and read it back.
   Record the tested/verified implementation SHA or merge SHA and tree equality when used.
4. Update PROJECT_STATE, backlog evidence/statuses only when supported, TEST_RESULTS and
   delivery/handoff records as applicable. Preserve incomplete work, blockers and Gates A/B.
5. Create a new immutable continuation prompt under `docs/continuations/`. Never overwrite
   an older continuation file. Naming should identify the phase/part transition and date.
6. Refresh `docs/NEXT_CHAT_PROMPT.md` so it points to and summarizes the newest immutable
   continuation. The next chat must still fetch the actual remote heads before writing.
7. Every continuation must contain: repository; active/next branch and PR if any; verified
   baseline/tested/merge SHA(s); files to read first; completed work; tests actually run;
   remaining task IDs/statuses; Gates A/B and external blockers; applicable ADRs; explicit
   work not to repeat; and the exact next implementation task.
8. Refresh ARTIFACT_MANIFEST/checksums and run bootstrap validation when repository
   conventions require it. Publish the continuity documentation and verify its remote head.
9. Only after the remote continuation is readable and verified may the previous chat stop
   writing. A documentation receipt may follow a tested implementation SHA; state that
   explicitly instead of pretending a self-referential final commit SHA can be embedded.

For recovery on another computer, start from `docs/NEXT_CHAT_PROMPT.md`, then open the
referenced immutable continuation and fetch the actual remote heads. GitHub state wins over
missing or device-local chat history.

