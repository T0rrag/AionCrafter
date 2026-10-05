Continue AionCrafter — Phase 06 manual-edition validation, Part 03.
Repository: https://github.com/T0rrag/AionCrafter
Branch: phase/06-release; draft PR #8 against main.
Immutable continuation:
docs/continuations/phase-06-part-02-to-part-03-2026-10-05.md

FIRST fetch and verify actual remote main/branch/PR heads and ancestry. Part 02 started
from 0f0c839ac93aebfef2841daadb4a3c18b2ec8db4; main was
e90c295b38245e57cf53a017d96885a770ed399f. Tested Part 02 implementation:
d01f575b2c4a88d802828820f0d1dd3f9c3f9ea7, tree
9eeae62900aa741e386735dfa72a46279d65aa67. Documentation follows that SHA.

Read AGENTS, PROJECT_STATE, the immutable continuation, handoffs/phase-06-part-02.md,
delivery/phase-06-part-02.json, backlog, TEST_RESULTS, PHASE_06_VALIDATION,
MANUAL_EDITION_GUIDE, ADR 0007–0010 and brief sections 14/20/21.

Part 02 delivered validated stored catalog JSON export and the changed-recipe
publish/export/web-start/compatibility/restore drill. GitHub Actions run 37310693174 on
the exact implementation SHA passed 269 tests on Python 3.12.14 plus compile, synthetic
catalog validation and bootstrap. Old plans/journals reject changed catalog content and
are not remapped; last-known-good backups recover prior observations, revisions/results.

Phase 06 remains IN_PROGRESS: p6-mathqa COMPLETE; p6-patches/security/package
IN_PROGRESS; p6-usertest/golive BLOCKED. Preserve p1-catalog and Phase 03 real-integration
blockers, Phase 04 remaining integration, Phase 05 DEFERRED and Gates A/B UNVERIFIED.

Exact next task: progress reproducible source packaging/installation evidence and measure
cached deterministic calculation performance against the brief's proposed <300 ms p95
target on declared hardware/runner and clearly SYNTHETIC data. Record warmup/sample
methodology. Do not invent a redistribution license or convert synthetic performance into
real-pilot evidence.

No Chromium troubleshooting, provider activation, Phase 05 work, automatic remapping,
visual QA/pilot/release claim, force-push or check bypass. Use the same branch/PR and one
writer. Before ending publish a NEW immutable continuation and refresh state, backlog/
progress, tests, handoff/delivery, guide as applicable, manifest and NEXT_CHAT_PROMPT;
verify remote SHA/tree/CI/PR state.
