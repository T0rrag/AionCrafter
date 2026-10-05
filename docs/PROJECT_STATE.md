# AionCrafter — Phase 06 manual-edition validation

2026-10-05 · Brief v1.3 / ADR 0007–0010. Phase 06 IN_PROGRESS, Part 02 delivered.
Gates A/B UNVERIFIED. All seven phases and 42 stable task IDs preserved.

## Repository and verified checkpoint

Repository: https://github.com/T0rrag/AionCrafter
Active branch: phase/06-release; target main. Draft PR #8 remains open/unmerged.
Verified base main at Part 02 start: e90c295b38245e57cf53a017d96885a770ed399f.
Verified Part 01 continuation head: 0f0c839ac93aebfef2841daadb4a3c18b2ec8db4.

Part 02 implementation checkpoint: d01f575b2c4a88d802828820f0d1dd3f9c3f9ea7.
Its Git tree is 9eeae62900aa741e386735dfa72a46279d65aa67, equal to the prebuilt
implementation tree used before publication. GitHub Actions run 37310693174 checked out
that exact SHA and completed successfully on Python 3.12.14. Documentation follows the
tested implementation and therefore the next writer must fetch actual heads.

## Delivered and tested

- p6-mathqa remains COMPLETE from Part 01.
- p6-patches now includes read-only `check-database`, no-overwrite SQLite `backup`,
  and `export-catalog` for a stored release. Export validates database kind, selected/
  active release existence, stored SHA-256, strict catalog payload validity and equality
  between the stored release key and payload release_id; it copies the exact stored JSON,
  rechecks the output digest and refuses overwrite.
- The new recovery drill publishes a changed synthetic recipe release, exports it, starts
  the local web app against that JSON, proves old saved plan and journal digests are
  rejected, verifies those rejection attempts do not rewrite rows, then restores the
  catalog/plans/ledger backups to NEW paths. The original JSON, observation, calculation,
  plan revision 2, journal revision 2 and ledger result are recovered. The changed working
  catalog remains untouched. No automatic remapping occurs.
- Part 01 security/recovery controls remain intact. A Phase 06 push workflow now gives
  reproducible Python 3.12 validation for this branch.

GitHub Actions run 37310693174 on Ubuntu 24.04 / Python 3.12.14:
`python -m unittest discover -q` — 269 passed in 18.910s;
compileall passed; synthetic catalog validation passed (7 items/3 recipes);
bootstrap passed with 42 stable IDs, 125 artifact checksums, 9 completed tasks with
evidence and Gates A/B unchanged. This is remote CI evidence for the synthetic/local
branch checkpoint, not real-game, visual, pilot, provider or release evidence.

## Remaining phase work and exact next task

p6-patches/security/package remain IN_PROGRESS. The independent next Part 03 work is
reproducible source packaging/installation evidence and a declared synthetic performance
measurement, while keeping licensing/distribution claims bounded to evidence. Do not
convert those checks into a public release claim.

p6-usertest is BLOCKED on permitted real data, a declared real market and 20 real
workflows. p6-golive is BLOCKED on applicable quality evidence. Visual/keyboard QA remains
deferred by the owner. Do not restart Chromium/cloud-browser troubleshooting.

## Preserved earlier work and external blockers

Phase 04 manual groundwork is merged; p4-batches/p4-ledger COMPLETE for independent
engineering, while p4-buycraft/proc/liquidity/rank remain IN_PROGRESS for real catalog/
rule/market integration and acceptance. Phase 03 remains IN_PROGRESS with real adapter/
reconciliation/activation BLOCKED. p1-catalog BLOCKED. Phase 05 DEFERRED.
Gates A/B UNVERIFIED. No provider permission, quota, fee or probability is invented.

No public release, deployment, real-game pilot, visual QA or automatic-provider activation
is claimed. GitHub is the durable continuity source; the next writer remains in Phase 06.
