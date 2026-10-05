# AionCrafter — Phase 06 manual-edition validation

2026-10-05 · Brief v1.3 / ADR 0007–0010. Phase 06 IN_PROGRESS, Part 01.
Gates A/B UNVERIFIED. All seven phases and 42 stable task IDs preserved.

## Repository and current writer

Repository: https://github.com/T0rrag/AionCrafter
Active branch: phase/06-release; target main. Draft PR #8: https://github.com/T0rrag/AionCrafter/pull/8. One repository writer in this chat;
supporting arithmetic/recovery/security reviews were read-only.
Verified starting main: e90c295b38245e57cf53a017d96885a770ed399f.
Remote phase/06-release was absent at startup; created from that main and now published.
PR #6 read-back confirmed merged at a185d0618cb315aa9468aec0de7716ccb1d56146 with
tested head e34ddf478c63777a0e0555664337d7eed2900134 in main ancestry. Only continuity
documentation differed from the Phase 04 implementation. Historical draft PRs #2/#3
are unchanged. No phase merge or release is implied by this checkpoint.

Tested/published implementation: 9f8128a84045f8ee1e24bd7c7d89b5efa984ff06.
Fetched tree equals the tested candidate: c8bc4bc7f5e22360f145b85be32c2b77f7d33774.
Receipt: delivery/phase-06-part-01.json. PR read-back confirms open/draft/unmerged.
NEXT_CHAT_PROMPT points to continuations/phase-06-part-01-to-part-02-2026-10-05.md.
This documentation receipt follows the implementation; fetch actual heads.

## Delivered and tested

- p6-mathqa: seven independent hand-calculated acceptance tests for monetary rounding
  at three precisions, shared-demand batch fees/inventory, unknown/zero distinctions,
  joint/failure/bonus outcomes with sale caps, bound outputs and exact FIFO allocation.
  Existing regressions remain; this calculation-regression requirement is COMPLETE.
- p6-patches: read-only `check-database` and no-overwrite `backup` commands for separate
  catalog, plan and ledger stores. Consistent per-file snapshots include committed WAL
  data; destination is standalone, validated and hashed. Restore drills preserve
  histories, observations, calculations, old-schema payloads and revision counters.
- p6-security: reproduced and fixed cross-store catalog migration, SQLite failures that
  disconnected local HTTP, malformed CSRF and UTF-8, stalled uploads and malformed paths.
  Inputs/valid journal preview survive storage failure. Catalog startup reads are bounded;
  plan migration ownership checks are transactional. SQLite sidecars stay out of Git.
- p6-package: source-checkout operating guide, update/backup/restore/retention guidance,
  factual attribution/license limits and release-evidence matrix. README now leads to
  the current phase instead of historical Phase 01 delivery instructions.

Final code validation on Windows/Python 3.12.14: 266 tests passed (17.177s), compileall
and synthetic catalog validation passed (7 variants/3 recipes). Implementation bootstrap passed: 42 IDs, 122 checksums. Remote implementation tree
equality is verified; receipt/continuation add two files to the final manifest. All new inputs are SYNTHETIC.
No visual/keyboard QA, real-game pilot, p95 benchmark or remote CI pass is claimed.
See PHASE_06_VALIDATION.md, MANUAL_EDITION_GUIDE.md and TEST_RESULTS.md.

## Remaining phase work and exact next task

p6-patches/security/package IN_PROGRESS: Part 01 evidence is bounded to local recovery
and review. Next Part 02 starts p6-patches: add an explicit validated catalog-release JSON
export and an end-to-end recipe-change recovery drill proving that the launched catalog
JSON and saved plan/journal digests agree before/after rollback. Do not automatically
remap mismatched records. Then continue reproducible package/installation evidence and
declared synthetic performance measurement, separate from real-pilot targets.

p6-usertest BLOCKED on permitted real data/declared market and the 20 real workflows;
p6-golive BLOCKED on applicable quality evidence. Visual/keyboard QA remains deferred
by the owner. Do not restart Chromium/cloud-browser troubleshooting.

## Preserved earlier work and external blockers

Phase 04 manual groundwork is merged; p4-batches/p4-ledger COMPLETE for independent
engineering. p4-buycraft/proc/liquidity/rank remain IN_PROGRESS for real catalog/rule/market
integration and acceptance. Phase 03 remains IN_PROGRESS with real adapter/reconciliation/
activation BLOCKED. p1-catalog BLOCKED. Phase 05 DEFERRED. Gates A/B UNVERIFIED.
No provider permission, quota, fee or probability is invented. Manual release does not
require optional Gates A/B, but its own quality criteria remain unfulfilled.

No public release, deployment, new chat creation or background continuation is claimed.
The next writer remains in Phase 06 and must verify GitHub continuity before writing.
