Continue AionCrafter Phase 02 — Manual calculator, Part 04 in this same Aion2 cloud
ChatGPT project. Use master prompt v1.3 sections 8/13/20/21 and ADRs 0003/0004.
Latest verified implementation: a3254c48831ea4cd54ce9e7211e286a9b3ca5f61.
Fetch T0rrag/AionCrafter phase/02-manual-calculator and verify actual head before writing.
Read docs/PROJECT_STATE.md, docs/handoffs/phase-02-part-03-acceptance.md, docs/backlog.json and
PHASE_02_ACCEPTANCE.md. PR #3 remains draft stacked on unmerged PR #2 (recorded base
3a395eb5894e65ff0d67e336d1a91dc452136843). Part 03 acceptance checkpoint passed 91 tests on Python 3.12.14.
Offline manual/vendor/snapshot imports and per-item observation ages are implemented;
unknown ages stay unknown, linked manual edits and plan transfers preserve provenance.
First: browser QA with an available Chromium, then remaining Phase 02 acceptance.
Visual attempts failed: local Chromium absent/download invalid; cloud loopback URL blocked.
Plan database v2 prevents stale writes after deletion/recreation; exact observations
survive repeated calculate/search/save. Review migration notes before upgrades.
All Phase 02 tasks IN_PROGRESS; Phase 01 incomplete/p1-catalog BLOCKED. Synthetic only.
Phases 03/05 DEFERRED; Gates A/B UNVERIFIED. Historical fees/realized profit unknown
without records; recursive optimization Phase 04. Inherited Python 3.14 warnings remain.
Develop/upload autonomously; no merge or force-push. Persist actual tests/handoff and
verify SHAs. This cloud continuation is canonical; local parent stopped code writes.
Create further same-project chats only at phase/context handoffs, verifying startup and
preventing concurrent writers. Do not claim local transcript synchronization.
