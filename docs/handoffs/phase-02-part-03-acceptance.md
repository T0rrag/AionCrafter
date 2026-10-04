# AionCrafter — Phase 02 / Part 03 acceptance checkpoint

Date: 2026-10-04. Brief v1.3, ADRs 0003/0004. Phase 02 IN_PROGRESS.
Branch phase/02-manual-calculator; draft PR #3 stacked on unmerged PR #2 at base
3a395eb5894e65ff0d67e336d1a91dc452136843. Started from verified remote
065dde81e685a5e80f8e3f12e8959d69b9b71d95. This continues the same canonical cloud chat.

## Delivered
p2-save: reproduced an old-tab overwrite after deleting/recreating the same plan name:
both old and recreated plans had revision 1. Database v2 now preserves a per-name revision
counter after deletion and rejects stale saves/deletes against a recreated plan. Migration
seeds counters from v1 revisions and preserves every existing payload. Only name/counter
metadata survives deletion; all saved contents/revisions are removed. Back up before upgrade;
older application versions that support only database v1 will refuse the upgraded database.

p2-editor/p2-save: calculate and search now carry the exact displayed observations into
subsequent posts/saves, retaining IDs, ingestion time and manual-override links. Source and
age appear beside every unit reference, including items outside the calculation. Merged
reference imports validate cross-item ID collisions before changing the preview.

Added four complete-form HTTP acceptance cases and two storage regressions. The form
helper submits real rendered controls instead of hand-selecting a subset of fields.
PHASE_02_ACCEPTANCE.md maps all six tasks to executed evidence and remaining review.

## Actual validation
Python 3.12.14 / Linux. Targeted form+plan suite: 13 passed. Full suite: 91 passed in
2.989 s. Compileall, offline synthetic catalog validation (7 items/3 recipes), diff check
and refreshed bootstrap manifest validation passed. Connected cloud browser navigation
to the running app failed with net::ERR_BLOCKED_BY_CLIENT. Earlier local Chromium was
missing and download invalid. Browser/visual acceptance remains UNVERIFIED; HTTP tests
do not substitute for it. Python 3.14 SQLite ResourceWarnings remain unresolved on that
runtime. No real game/pilot/provider/overlay/Windows/remote CI claims.

## Constraints and next action
All 42 IDs preserved; all Phase 02 tasks IN_PROGRESS. Phase 01 incomplete/p1-catalog
BLOCKED; Phases 03/05 DEFERRED; Gates A/B UNVERIFIED. Synthetic only. Direct ingredients;
recursive optimization is Phase 04. Actual historical craft/sale fees and realized profit
remain unknown without records. No merge or force-push.

Next: execute the documented visual workflow checks in a browser-capable environment and
obtain owner/pilot acceptance. No additional cloud chat created at this checkpoint; the
current context is usable. No callable chat-creation capability was found in the available
tool catalog. User authorization persists for a future supported same-project handoff;
do not invent creation or run concurrent branch writers. Local parent remains stopped.
Read PROJECT_STATE.md, this handoff, PHASE_02_ACCEPTANCE.md and selected code/tests.
