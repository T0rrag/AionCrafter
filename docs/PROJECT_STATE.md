# AionCrafter — project state

Checkpoint: 2026-10-04 · Phase 02 / Part 03, acceptance continuation · Brief v1.3, ADRs 0003/0004.
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
Starting delivery head for this continuation: `065dde81e685a5e80f8e3f12e8959d69b9b71d95`.
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
| p2-economics | IN_PROGRESS | Integer units, rational ROI/break-even, deterministic batches and configurable fee/rounding assumptions. 11 economics tests include joint outputs and multiple fees. Owner/game-rule acceptance pending. |
| p2-editor | IN_PROGRESS | Offline manual/vendor/snapshot references; rights/type/scope validation; linked overrides; per-item source/age and unknown timestamps; exact displayed provenance retained. Browser/source acceptance pending. |
| p2-listflow | IN_PROGRESS | Selected or pasted materials, ambiguity picker, known subtotal/incomplete total. Full-form HTTP acceptance passed. Visual/pilot review pending. |
| p2-itemflow | IN_PROGRESS | English/Spanish alias search, recipe/product selection, direct ingredients, batch yield/leftovers and margins; full-form save acceptance passed. Visual/pilot review pending. |
| p2-costmodes | IN_PROGRESS | Owned stock reduces cash but preserves replacement cost; supplied consumed-material records require complete coverage. Owner/pilot acceptance pending. |
| p2-save | IN_PROGRESS | Local immutable plan revisions, favorites/settings/inventory; validated JSON/CSV, preview/reset/confirmed deletion. v2 migration and delete/recreate stale-tab regression passed. Visual/owner acceptance pending. |

See `PHASE_02_ACCEPTANCE.md` for exact cases and remaining review procedure.

## Validation and limits

Linux/Python 3.12.14: `python3 -m unittest discover -q` — **91 passed**.
Targeted complete-form + plan suite — 13 passed. Compileall, offline catalog validation,
diff checks and refreshed bootstrap manifest checks passed. Tests parse and submit
actual rendered controls over loopback HTTP; no browser layout/keyboard claim follows.

Visual QA remains **UNVERIFIED**. Prior local Chromium was absent and downloads returned
invalid ZIPs. Connected cloud browser was also tried against the running calculator:
`net::ERR_BLOCKED_BY_CLIENT`. No screenshot or rendered-page acceptance obtained.
Prior Python 3.14 SQLite ResourceWarnings remain unresolved on that runtime. No remote
CI, Windows, pilot/game, live-provider or overlay success claimed.

Fixtures remain **SYNTHETIC ONLY** (7 variants, 3 recipes); no permitted real catalog.
p1-catalog still needs pilot scope, rights, 100 real items and 25 verified recipes.
Unknown stochastic outcomes are rejected. Leftovers/coproducts have no revenue credit;
all craft costs go to planned sales. Per-output-unit fees count every produced output;
per-attempt/per-batch each count an invocation. Tax rounding applies once to batch
proceeds as an unverified assumption. Vendor stock, restrictions and sell-through stay
manual checks. Actual historical craft/sale fees and realized profit are unknown without
records. Recursive optimization remains Phase 04.

## Next action and continuity

Continue Phase 02 acceptance in this cloud chat while context is practical. Execute the
visual workflow matrix where a browser can reach the loopback app, then obtain owner
and permitted pilot review. Read `handoffs/phase-02-part-03-acceptance.md`.
`NEXT_CHAT_PROMPT.md` prepares a future Part 04 continuation; it does not create a chat.
No callable chat-creation tool was found this turn. User authorization for autonomous
uploads and same-project chat handoffs persists, subject to verifying actual startup
and preventing concurrent writers. Do not start another phase or mark this one complete
just because automated engineering tests passed.
