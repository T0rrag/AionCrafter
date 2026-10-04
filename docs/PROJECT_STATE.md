# AionCrafter — project state

Checkpoint: 2026-10-04 · Phase 02 / Part 03, acceptance continuation · Brief v1.3, ADRs 0003–0005.
Phase 02 **IN_PROGRESS**; Phase 01 **IN_PROGRESS**, p1-catalog **BLOCKED**.
Phases 03/05 **DEFERRED**; Gates A/B **UNVERIFIED**. All 42 task IDs retained.

## Repository and active writer

https://github.com/T0rrag/AionCrafter · branch `phase/02-manual-calculator`.
Draft PR #3: https://github.com/T0rrag/AionCrafter/pull/3, explicitly stacked on
unmerged PR #2; base `phase/01-data-foundation` at
`3a395eb5894e65ff0d67e336d1a91dc452136843`.
This existing Aion2 cloud Work chat is the canonical active continuation, designated
by the user. The local parent stopped application writes. GitHub provides durable code
and handoff state; old local transcripts are not automatically synchronized or converted.
No merge, force-push, release, deployment or permission changes.

## Published baseline and current increment

Part 02 implementation: `4594c5a6c825733bd49c56c14cddfd41a3161ab7` (77 tests).
Part 03 reference implementation: `f8274ad71267a7737a95cff40e45eb9f7c9fb431` (85 tests).
Acceptance implementation: `a3254c48831ea4cd54ce9e7211e286a9b3ca5f61` (91 tests); fetched tree matches tested checkpoint.
Previous acceptance starting head: `065dde81e685a5e80f8e3f12e8959d69b9b71d95`.
Reference acceptance implementation: `d355f7107d0a2205a61afc672f7c27f9b2146864` (95 tests), started from actual remote
`c70d5578c3590d22b9d582f7ca8a16895a8171a8`, which superseded the requested 4797ce5 baseline.
Fetched implementation tree equals the tested working tree. Existing observation IDs
can be replayed identically but cannot change any displayed record; replacements need
new IDs. Subsecond future observations are explicitly flagged.
Each published implementation was fetched and matched its tested local tree. Delivery
receipts follow code; always fetch actual head before writes. Publication uses connected
GitHub tree/commit/ref updates with force:false; HTTPS fetch verifies tree equality.

Current increment fixes stale saves/deletes after a plan name is deleted/recreated,
preserves displayed observations through consecutive calculate/search/save actions,
shows source/age at each price input and rejects merged import ID collisions atomically.
Plan database migrates v1→v2 without altering existing payloads. Deletion removes saved
content while retaining a per-name revision counter. Back up before upgrading; old
v1-only applications cannot reopen a v2 plan database. JSON/CSV plan schema stays v1.

## Task evidence and remaining acceptance

| Task | Status | Implemented evidence / remaining work |
|---|---|---|
| p2-economics | IN_PROGRESS | Integer units, rational ROI/break-even, deterministic batches and configurable fee/rounding assumptions. 11 economics tests include joint outputs and multiple fees. Owner behaviour accepted; game-rule validation deferred to final pilot. |
| p2-editor | IN_PROGRESS | Offline manual/vendor/snapshot references; rights/type/scope validation; linked overrides; per-item source/age and unknown timestamps; exact displayed provenance retained. Browser/source acceptance pending. |
| p2-listflow | IN_PROGRESS | Selected or pasted materials, ambiguity picker, known subtotal/incomplete total. Full-form HTTP acceptance passed. Visual/pilot review pending. |
| p2-itemflow | IN_PROGRESS | English/Spanish alias search, recipe/product selection, direct ingredients, batch yield/leftovers and margins; full-form save acceptance passed. Visual/pilot review pending. |
| p2-costmodes | IN_PROGRESS | Owned stock reduces cash but preserves replacement cost; supplied consumed-material records require complete coverage. Owner behaviour accepted; final pilot deferred. |
| p2-save | IN_PROGRESS | Local immutable plan revisions, favorites/settings/inventory; validated JSON/CSV, preview/reset/confirmed deletion. v2 migration and delete/recreate stale-tab regression passed. Owner behaviour accepted; visual QA deferred. |

See `PHASE_02_ACCEPTANCE.md` for exact cases and remaining review procedure.

Latest owner clarification (2026-10-04, ADR 0005 addendum): the user marked PR
review/closure "Done" in chat; no GitHub review/closure or merge was performed.
The user then confirmed the calculator behaves correctly: owner behaviour acceptance
is complete. The user's
customization comment is treated as a presentation/controls requirement with details
unspecified; existing fee/tax/rounding settings are configurable. Visual/keyboard QA
remains deferred and unverified. Real-game pilot validation is scheduled after all
phase feature work, under p6-usertest, rather than as a Phase 02 development blocker.
The pending acceptance entries above must be read with this revised timing.

## Validation and limits

Linux/Python 3.12.14: `python3 -m unittest discover -q` — **95 passed**.
Latest targeted form + reference suite — 14 passed (previous form + plan suite: 13). Compileall, offline catalog validation,
diff checks and refreshed bootstrap manifest checks passed. Tests parse and submit
actual rendered controls over loopback HTTP; no browser layout/keyboard claim follows.

Visual QA remains **UNVERIFIED**. Prior local Chromium was absent and downloads returned
invalid ZIPs. Connected cloud browser was also tried against the running calculator:
`net::ERR_BLOCKED_BY_CLIENT`. No screenshot or rendered-page acceptance obtained.
Prior Python 3.14 SQLite ResourceWarnings remain unresolved on that runtime. GitHub check-runs and Actions runs for the starting head returned zero entries; no remote
CI success, Windows, pilot/game, live-provider or overlay success claimed.

Fixtures remain **SYNTHETIC ONLY** (7 variants, 3 recipes); no permitted real catalog.
p1-catalog still needs pilot scope, rights, 100 real items and 25 verified recipes.
Unknown stochastic outcomes are rejected. Leftovers/coproducts have no revenue credit;
all craft costs go to planned sales. Per-output-unit fees count every produced output;
per-attempt/per-batch each count an invocation. Tax rounding applies once to batch
proceeds as an unverified assumption. Vendor stock, restrictions and sell-through stay
manual checks. Actual historical craft/sale fees and realized profit are unknown without
records. Recursive optimization remains Phase 04.

## Next action and continuity

User direction (2026-10-04, ADR 0005): continue normal feature development and create a
new chat for each phase. Remove cloud/Chromium troubleshooting from the active queue.
Next eligible development phase: **Phase 04 — Crafting intelligence**, Part 01, starting
with **p4-batches**. The tested Phase 02 engineering is a sufficient dependency for
synthetic Phase 04 work. Its visual/pilot acceptance remains recorded for later
review; these pending checks do not block the next engineering phase or become passed.

Read `handoffs/phase-02-to-phase-04.md` and `decisions/0005-continue-engineering-without-browser-gate.md`.
`NEXT_CHAT_PROMPT.md` starts Phase 04. Use `phase/04-crafting-intelligence`, explicitly
stacked on unmerged Phase 02 PR #3. Fetch actual remote branch/head before writing.
This Phase 02 chat stops application writes at handoff. A separate same-project chat
must be created/verified before claiming Phase 04 started there. No merge/force-push.

The fetched current code baseline was rerun: **95 tests passed**, Python 3.12.14.
This checkpoint updates sequencing/documentation only; prior feature evidence stands.
