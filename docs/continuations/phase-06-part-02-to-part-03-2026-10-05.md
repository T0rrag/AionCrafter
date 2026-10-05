# AionCrafter continuation — Phase 06 Part 02 to Part 03

Date: 2026-10-05
Repository: https://github.com/T0rrag/AionCrafter
Active/next branch: phase/06-release; base main.
Active PR: https://github.com/T0rrag/AionCrafter/pull/8 — keep the same PR.
Canonical moving entry: docs/NEXT_CHAT_PROMPT.md.

## Verified checkpoint

- Part 02 started from phase/06-release
  `0f0c839ac93aebfef2841daadb4a3c18b2ec8db4`.
- Main at Part 02 start: `e90c295b38245e57cf53a017d96885a770ed399f`.
- Tested implementation: `d01f575b2c4a88d802828820f0d1dd3f9c3f9ea7`.
- Tested/prebuilt implementation tree:
  `9eeae62900aa741e386735dfa72a46279d65aa67`.
- GitHub Actions run 37310693174 checked out that exact SHA and succeeded.
- This continuation follows the implementation in documentation-only commits. Fetch the
  actual main/branch/PR heads and compare ancestry before any next write.

## Read first

AGENTS.md; docs/PROJECT_STATE.md; docs/NEXT_CHAT_PROMPT.md; this continuation;
docs/handoffs/phase-06-part-02.md; docs/delivery/phase-06-part-02.json;
docs/backlog.json; docs/TEST_RESULTS.md; docs/PHASE_06_VALIDATION.md;
docs/MANUAL_EDITION_GUIDE.md; ADR 0007–0010; AionCrafter_Project_Prompt.md sections
14, 20 and 21. For code, inspect database.py, __main__.py, tests/test_recovery.py and
the Phase 06 validation workflow before expanding scope.

## Delivered in Part 02

`export-catalog` exports the active or selected release from a recognized catalog
database without migration. It verifies stored SHA-256, strict catalog payload validity
and release key/payload identity, writes exact stored JSON bytes to a NEW path, verifies
the output hash and refuses overwrite.

The synthetic recipe-change recovery drill:
1. saves catalog observations/calculation plus plan/journal revision histories;
2. exports and backs up the last-known-good set;
3. publishes a new release with changed recipe content;
4. exports and starts the local web process with that changed JSON;
5. proves old plan/journal catalog digests are rejected and their rows are unchanged;
6. restores catalog/plans/ledger to NEW paths;
7. re-exports the original JSON byte-for-byte and recovers observation, calculation,
   plan revision 2, journal revision 2 and the prior ledger result.
No record identity or probability evidence is remapped automatically.

## Actual validation

GitHub Actions run 37310693174, Ubuntu 24.04 / CPython 3.12.14:
- 269 unit tests passed in 18.910s.
- compileall passed.
- synthetic catalog validation passed: 7 items / 3 recipes.
- bootstrap passed: 42 stable IDs, 125 artifact checksums, 9 completed tasks with
  evidence, Gates A/B UNVERIFIED.

This is real remote CI evidence for the synthetic/local checkpoint. It is not a real-game
pilot, provider integration, visual/keyboard QA, performance benchmark or release.

## Status boundaries

Phase 06 remains IN_PROGRESS.
- p6-mathqa COMPLETE.
- p6-patches, p6-security, p6-package IN_PROGRESS.
- p6-usertest BLOCKED.
- p6-golive BLOCKED.
p1-catalog BLOCKED. Phase 03 real integration BLOCKED/IN_PROGRESS. Phase 04 real
integration incomplete. Phase 05 DEFERRED. Gates A/B UNVERIFIED.
Keep all 42 IDs unchanged.

## Exact next implementation task

Continue Phase 06 Part 03 on this SAME branch and PR. Build reproducible
source-checkout/package installation evidence without inventing a redistribution license,
then measure cached deterministic calculation latency against the brief's proposed
**<300 ms p95** target on explicitly declared hardware/runner and a clearly SYNTHETIC
dataset. Record methodology, sample count, warmup and result; keep this evidence separate
from real pilot performance. If packaging is constrained by the unresolved license, test
only the reproducible source artifact/installation path and document the blocker.

Do not activate a real provider, begin Phase 05, restart Chromium/cloud-browser
troubleshooting, claim a pilot/release, or remap incompatible records. Preserve visual QA
deferral and all real-catalog/integration blockers.

Before Part 03 ends, create a NEW immutable continuation and refresh NEXT_CHAT_PROMPT,
PROJECT_STATE, backlog/progress, TEST_RESULTS, handoff/delivery, manifest and applicable
guides. Run the required tests/validators, publish only tested checkpoints, verify remote
SHAs/tree and PR state, then stop the previous writer.
