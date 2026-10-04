# AionCrafter — Phase 02 / Part 03 handoff
Date: 2026-10-04. Brief v1.3; ADRs 0003/0004. Phase 02 IN_PROGRESS.
Repository T0rrag/AionCrafter; branch phase/02-manual-calculator; draft PR #3 stacked
on unmerged PR #2, base 3a395eb5894e65ff0d67e336d1a91dc452136843.
Started from actual verified head 4797ce5f5fd46fcf6055afc1357802cf02d55303.

## Delivered and verified
p2-editor: references.py and web.py support offline JSON PriceObservation arrays with
manual/vendor-purchase/snapshot distinctions, exact catalog variant and market/currency
matching, recorded permission references, duplicate/type/rights rejection and preview.
No external source was fetched or approved by this code. Synthetic sample only.
Per-item observation times allow mixed-age references and unknown snapshot/vendor times.
Source, rights, observed/ingested times and actual observation age appear in result rows.
Snapshots are delayed references, never live. Stock/vendor restrictions remain manual.
Edits create linked manual observations; unchanged references retain immutable provenance.
p2-save: reference observations survive calculate/save/load and JSON/CSV transfers.
p2-economics: broader joint-output/multiple-fee/wrong-currency/negative-proceeds tests.
Actual historical craft/sale fees and realized profit remain unknown without records.

## Actual tests
Python 3.12.14, Linux. python3 -m unittest discover -q: 85 passed (77 inherited + 8 new).
python3 -m compileall -q aioncrafter tests passed.
python3 -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json passed: 7/3.
git diff --check and scripts/validate_bootstrap.py passed after manifest refresh.
HTTP tests exercise reference import, calculate, save/reload with unchanged source.
Visual browser QA attempted: Playwright Chromium executable absent; installation failed
with invalid/truncated ZIP archives. No screenshot or visual acceptance obtained.
Inherited Python 3.14 SQLite ResourceWarnings were not reproduced/tested on that runtime
and remain unresolved. No game/pilot/provider/overlay/Windows/remote-CI claim.

## Cloud continuity and constraints
User explicitly designated this existing Aion2 cloud chat canonical; local parent stopped
application writes. Updated superseded cloud-choice-pending state. GitHub is durable code
and state handoff, not automatic local transcript synchronization. Continue here while
context is practical; no additional chat was created or needed for this checkpoint.
All 42 backlog IDs retained. All Phase 02 tasks stay IN_PROGRESS pending acceptance;
Phase 01 incomplete/p1-catalog BLOCKED; Phases 03/05 DEFERRED; Gates A/B UNVERIFIED.
No merge/force-push. Direct ingredients only; recursive optimization stays Phase 04.

## Next
Browser QA in an environment with Chromium, owner acceptance of fee/reference semantics
and permitted pilot validation. Read PROJECT_STATE.md, REFERENCE_IMPORTS.md, backlog.json,
this handoff, ADRs 0003/0004 and relevant code/tests. Fetch actual head before writes.
Use NEXT_CHAT_PROMPT.md only when a future context handoff is needed; avoid concurrent writers.
