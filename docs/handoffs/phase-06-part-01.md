# AionCrafter — Phase 06 / Part 01 handoff

Date: 2026-10-05. Brief v1.3. Phase status: IN_PROGRESS.
Repository: T0rrag/AionCrafter. Branch: phase/06-release; base main.
Verified starting main: e90c295b38245e57cf53a017d96885a770ed399f.
Draft PR #8: https://github.com/T0rrag/AionCrafter/pull/8.
Tested/published SHA: 9f8128a84045f8ee1e24bd7c7d89b5efa984ff06; fetched tree
c8bc4bc7f5e22360f145b85be32c2b77f7d33774 equals tested candidate.
Publication receipt: docs/delivery/phase-06-part-01.json. Documentation follows tested SHA.

## Delivered and verified

p6-mathqa now has seven hand-calculated acceptance tests, including nine currency-scale/
rounding combinations, shared demand and joint-output fees, owned stock, unknown/zero
prices, stochastic outcomes/bonus caps, bound-sale refusal and FIFO fractional allocations.
The existing 238-test baseline passed before edits; the final code suite has 266 tests.
The calculation-regression task is COMPLETE, without claiming game-rule correctness.

p6-patches adds offline `check-database` and `backup` commands. Backups use read-only
source access and SQLite snapshots, include committed WAL data and produce a standalone
destination with integrity/schema checks and SHA-256. Existing files or sidecars are
refused. Thirteen recovery tests verify legacy migrations on copies only, full catalog/
plan/journal history, restored rollback, revision conflicts, invalid sources, cleanup and
CLI behavior. Payload validity remains separate from structural integrity.

p6-security fixes three reproduced failures: catalog migration of another store, broken
HTTP responses from corrupt storage, and non-ASCII CSRF exceptions. Eight local HTTP
regressions cover input preservation, journal previews, disk failure, tokens/UTF-8,
malformed paths, stalled uploads and Host/Origin/privacy headers. p6-package adds the
operating guide and release checklist. Text is LF for portable manifest checksums.

## Tests actually run

Windows/Python 3.12.14: `python -m unittest discover -q` — 266 passed in 17.177s.
`python -m compileall -q aioncrafter tests` passed.
`python -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json` passed: 7 items,
3 recipes. Implementation diff/bootstrap passed (42 IDs, 122 hashes); fetched-tree verification
is recorded in the delivery receipt. Final receipt/continuation add two manifest entries. These are synthetic/local tests, not visual
QA, game pilot, remote CI or measured performance. Initial focused recovery/security
and seven-test math runs also passed before final added regressions.

## Decisions, boundaries and remaining work

Read ADR 0010 and PHASE_06_VALIDATION.md. One writer; agents reviewed read-only.
Snapshots are per-file, so stop writers for a related backup set. The web process uses
catalog JSON, not the CLI active pointer. Preserve exact prior JSON with plan/ledger files;
their digests must match. Store guards accept legacy catalog schema1/2 without rewriting
payloads. No forced ref movement, provider connection or automatic record remapping.

p6-patches/security/package remain IN_PROGRESS. p6-usertest/golive are BLOCKED on real
pilot and applicable quality evidence. Phase 03 real integration and p1-catalog BLOCKED;
Phase 04 real integration incomplete; Phase 05 DEFERRED; Gates A/B UNVERIFIED.
Visual/keyboard QA remains deferred. Do not restart Chromium troubleshooting or treat
the guide/checkpoint as a released product. No phase merge is needed for this partial PR.

## Next session

Phase 06 Part 02, same branch and PR. First add validated catalog-release JSON export
and a recipe-change recovery drill: switch catalog, prove plan/journal mismatch refusal,
restore last known-good JSON/backups and prove the original workflows recover. Then
address reproducible packaging/installation and declared synthetic performance evidence.
Read AGENTS, PROJECT_STATE, NEXT_CHAT_PROMPT and its immutable continuation, this handoff,
backlog, ADR 0007–0010, operating guide, validation matrix and delivery receipt first.
Fetch actual refs; the receipt records tested SHA, not a guarantee of latest head.
