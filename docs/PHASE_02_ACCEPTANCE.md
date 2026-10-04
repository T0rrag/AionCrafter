# Phase 02 acceptance evidence

2026-10-04 · Part 03 continuation · Linux / Python 3.12.14.
Engineering checks use only the permitted, explicitly SYNTHETIC fixtures. This record
is not owner sign-off or an in-game pilot. All six Phase 02 tasks remain IN_PROGRESS.

| Task | Executed evidence | Outstanding acceptance |
|---|---|---|
| p2-listflow | Complete rendered HTML forms posted over loopback HTTP; materials total 36.90 for 3 × 12.30; missing price remains incomplete; fully owned demand needs 0.00 additional cash | Visual layout, keyboard interaction and permitted pilot |
| p2-itemflow | Full-form product/recipe workflow; target 3, 2 crafts, 4 produced, 1 leftover; successful saved plan; bilingual search retains price observations | Browser interaction and owner/pilot validation; recursion is Phase 04 |
| p2-editor | Mixed snapshot with unknown time/vendor with known old time; per-field source labels; linked manual price edit gives total 45.00; repeated calculate/search retains exact observations; cross-item ID collision refused before applying import | Visual readability and source/age review; no approved real source supplied |
| p2-costmodes | Missing reference + owned quantity preserves unknown replacement value and known zero cash; historical costs remain incomplete without complete records | Owner/pilot review; actual fee and realized-profit ledger is later scope |
| p2-economics | 11 exact-arithmetic tests include all three joint-output fee bases, multiple fees, wrong currency, fixed fees exceeding proceeds, minimal break-even ticks | Owner acceptance of declared assumptions; no game fee rules verified |
| p2-save | Full-form save/load/CSV import-copy preserves observations; stale save/delete rejected after delete/recreate; v1 database migrates with payload unchanged; existing reset, deletion, CSRF and import validation tests remain passing | Visual workflow/keyboard checks and owner acceptance |

## Commands and results

- `python3 -m unittest tests.test_form_acceptance tests.test_plans -q`: 13 passed.
- `python3 -m unittest discover -q`: 91 passed, 2.989 seconds; no failures/skips.
- `python3 -m compileall -q aioncrafter tests`: passed.
- `python3 -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json`: 7 items, 3 recipes, SYNTHETIC.
- `git diff --check`: passed.
- `python3 scripts/validate_bootstrap.py`: passed after updating the manifest.

The form test helper parses actual inputs/selects/textareas and submits their values.
It does not render CSS, execute browser constraint validation, measure layout or test
keyboard focus. It is HTTP acceptance evidence, not visual/browser acceptance.

## Browser attempts

Earlier local Playwright: browser executable absent; official Chromium download returned
invalid ZIP archives. This continuation also tried the connected cloud browser against
the running loopback calculator; navigation failed with `net::ERR_BLOCKED_BY_CLIENT`.
No page rendering, screenshot, or visual pass was obtained. No policy was weakened and
no public deployment was introduced to get around this limitation.

## Remaining review procedure

In an environment that can open the loopback application, launch the README command
with a separate test `--plans` database. Check both workflows, pasted ambiguous aliases,
English/Spanish search, mixed reference ages, manual overrides, missing prices, saved
plan reset/reload, JSON/CSV transfers and two tabs editing the same plan. Inspect layout
at 1080p/1440p, keyboard-only controls, errors and narrow windows. Record actual browser,
viewport, results and screenshots. This procedure has not yet been executed visually.
Owner review and a permitted pilot catalog remain external acceptance requirements.
Inherited Python 3.14 SQLite ResourceWarnings remain unresolved on that runtime.

## Reference import acceptance extension — 2026-10-04

Implementation d355f7107d0a2205a61afc672f7c27f9b2146864 was fetched and its complete
working tree matched the tested checkpoint. Started at c70d5578c3590d22b9d582f7ca8a16895a8171a8.
Existing displayed observation IDs reject changed price, type or ingestion time; exact
replay is idempotent. Mixed imports fail atomically, retaining current form and saved plan.
Full-form HTTP tests reject wrong market, vendor sell-back as acquisition, and malformed
synthetic rights. Zero snapshots give a known 0.00 total; unavailable snapshots give
Incomplete. Age tests cover timezone offsets and future/subsecond clock discrepancy.
This ID check covers records in the current preview, not a global source history registry.

Latest commands: `python3 -m unittest tests.test_form_acceptance tests.test_references -q`
— 14 passed; `python3 -m unittest discover -q` — 95 passed, 4.608 seconds, Linux/Python
3.12.14. Compileall, synthetic catalog validation and diff checks passed; bootstrap
validator passed with 42 IDs and 62 artifact checksums. Local Playwright launch was tried
again: Chromium executable absent (chromium_headless_shell-1234). No browser rendering
was obtained; previous connected-browser loopback blockage remains recorded above.
Visual/browser, owner and permitted pilot acceptance remain outstanding.

## Sequencing update — ADR 0005

The user directed normal development on 2026-10-04 and asked to ignore the ongoing
cloud/Chromium work. The outstanding visual/owner/pilot acceptance above remains an
evidence record, not the next engineering task. Proceed to Phase 04 in a new Aion2 chat
using the tested Phase 02 foundation. No test is promoted to passed by this decision.
