# AionCrafter continuation — Phase 06 Part 01 to Part 02

Date: 2026-10-05
Repository: https://github.com/T0rrag/AionCrafter
Active/next branch: phase/06-release; base main.
Active PR: https://github.com/T0rrag/AionCrafter/pull/8 — OPEN, DRAFT, UNMERGED.
Canonical moving entry: docs/NEXT_CHAT_PROMPT.md.

## Verified checkpoint

- Starting/last observed main: e90c295b38245e57cf53a017d96885a770ed399f.
- Tested and published Part 01 implementation: 9f8128a84045f8ee1e24bd7c7d89b5efa984ff06.
- Tested/fetched implementation tree: c8bc4bc7f5e22360f145b85be32c2b77f7d33774.
- GitHub tree creation matched the staged tree; HTTPS fetch returned the implementation
  SHA and complete staged/working-tree comparison matched. No force-push or merge.
- PR read-back: same head/base, draft=true, merged=false, mergeable=true.
- Status/check-run/workflow queries for implementation returned zero entries; reviews
  were empty. Combined status pending with no entries is NOT a CI pass.
- This immutable continuation is a documentation receipt after the tested implementation.
  It intentionally does not embed its own future commit SHA. Fetch actual remote heads
  and compare ancestry; the tested SHA is a verified baseline, not necessarily latest head.

## Read first

AGENTS.md; docs/PROJECT_STATE.md; docs/NEXT_CHAT_PROMPT.md; this continuation;
docs/handoffs/phase-06-part-01.md; docs/delivery/phase-06-part-01.json;
docs/backlog.json; docs/TEST_RESULTS.md; docs/PHASE_06_VALIDATION.md;
docs/MANUAL_EDITION_GUIDE.md; ADR 0007, 0008, 0009 and 0010;
AionCrafter_Project_Prompt.md sections 14, 20, 21.
For implementation inspect database.py, storage.py, __main__.py, plans.py, ledger.py,
web.py and tests/test_recovery.py/test_security_recovery.py/test_math_acceptance.py.
Retain Phase 04 contracts when touching catalog or economics behavior.

## Completed work and actual tests

p6-mathqa COMPLETE for the regression requirement: seven independent hand-calculated
tests derive rounding at scales0/2/3, shared demand/joint fees, owned stock, missing/zero
values, scenarios/failure/bonus sale caps, unknown probability, bound outputs and FIFO.

p6-patches includes read-only database checks and consistent no-overwrite per-file SQLite
backups with standalone destinations and SHA-256. Thirteen recovery tests preserve
catalog/plan/journal histories, legacy sources, restored migrations/rollback, revision
counters and WAL commits; reject foreign/corrupt/future sources and occupied destinations,
including orphaned sidecars. Structural integrity is not typed-payload validation.

Focused security fixes reject cross-store migrations and malformed CSRF/UTF-8; SQLite
failures preserve unsaved input/valid journal previews. Eight HTTP regressions cover
storage errors, request guards, malformed paths, headers and stalled reads. Catalog
startup uses bounded reads; plan checks are transactionally serialized. The operating
guide covers installation, updates, backup/restore, retention, limitations and attribution.
Text is LF for portable manifest checksums; original brief/roadmap/old continuation Git
content is unchanged. See ADR 0010.

Windows/Python 3.12.14:
- Baseline: python -m unittest discover -q — 238 passed in 10.576s.
- Final code: same command — 266 passed in 17.177s (28 new tests).
- python -m compileall -q aioncrafter tests — passed.
- python -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json — passed,
  7 variants/3 recipes.
- git diff --check — passed.
- Implementation bootstrap validator — 42 stable IDs, 122 checksums.
  Receipt adds this prompt and delivery JSON; final manifest is checked before upload.

No real game/client, visual/keyboard QA, p95 benchmark, remote CI, production security
approval, new chat startup or public release is claimed. Fixtures/evidence are SYNTHETIC.

## Remaining statuses and boundaries

Phase 06 IN_PROGRESS:
- p6-mathqa COMPLETE.
- p6-patches, p6-security, p6-package IN_PROGRESS.
- p6-usertest BLOCKED on permitted real catalog/market and 20 real pilot cases.
- p6-golive BLOCKED on applicable quality evidence, including pilot and packaging;
  deferred visual/keyboard QA and unmeasured performance remain explicit.

All 42 IDs preserved. p1-catalog BLOCKED. Phase 03 real adapter/reconciliation/activation
BLOCKED and phase IN_PROGRESS. Phase 04 real-rule/catalog/market integration incomplete;
p4-batches/p4-ledger independent engineering COMPLETE. Phase 05 DEFERRED.
Gates A/B UNVERIFIED. Optional gates alone do not block a future manual release, but its
own applicable criteria are unfinished. Source permission precedes real connection.

## Exact next implementation task

Continue Phase 06 Part 02 on the SAME branch and PR after verifying remote main/branch/
PR heads. First p6-patches: add an explicit catalog-release JSON export that validates
the saved release/checksum and refuses overwriting an output. Add an end-to-end
recipe-change recovery drill: publish a changed catalog, export/start against its JSON,
prove old saved plan/journal digest mismatch is refused, then restore the last known-good
catalog JSON and backup set and verify original observations/revisions/results recover.
Do not automatically rewrite mismatched plan/journal identities or probability evidence.

Then progress reproducible source packaging/installation and declared synthetic
performance evidence as separate bounded Phase 06 work. Retain the license decision
and real-catalog/pilot as unresolved external inputs; never invent a license or game data.

## Do not repeat or cross

Do not rebuild delivered Phase 04 features, restart Chromium/cloud-browser troubleshooting,
activate automatic providers, add overlay work, merge old draft PRs, or declare a release.
Do not treat catalog SQLite rollback as changing the web JSON or a running process.
Back up each existing store and exact catalog JSON with writers stopped; restore to NEW
paths and match the ledger path to the selected plans path. No forced push, concurrent
overwrite, required-check bypass, permission/visibility change or unsupported schema edits.
One active repository writer. Current Part 01 writer stops after verified receipt.

At the next handoff create a NEW immutable docs/continuations/ file; never overwrite this
one. Refresh NEXT_CHAT_PROMPT, PROJECT_STATE, backlog/progress, tests, delivery/handoff
and manifest, publish and verify remote SHA/tree, then stop the previous writer.
