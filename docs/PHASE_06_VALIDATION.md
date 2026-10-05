# Phase 06 — Manual-edition validation, Part 01

2026-10-05. All new fixtures are **SYNTHETIC**. Monetary values in the tables below
are integer minor currency units unless written as decimal input strings. Fractions
are exact; no Decimal context or floating-point tolerance defines expected results.

## Hand-calculated acceptance

`tests/test_math_acceptance.py` supplies literal expected values independent of the
implementation. The existing brief example remains in `test_economics.py`.

| Case | Independent derivation and expected result |
| --- | --- |
| Currency scales 0, 2 and 3 | One minor unit material; one sold at one minor unit, 50% tax, one minor fixed fee. Net before fee = 1/2: floor gives proceeds -1, profit -2; ceil/half_up gives proceeds 0, profit -1. Unrounded break-even is 4; minimum integer sale price is 4 for floor and 3 for ceil/half_up. Nine scale/rounding combinations. |
| Shared demand and joint outputs | Three final units need left3 and right3. Left uses bar6; right batches round to2, producing right4 and using bar6. Shared needs bar12: three batches of ore3 → bar4+dust1. Thus ore9, dust3/right1 leftover. Fees: 15 output units × .07 + 3×.11 + 2×.13 + 3×.17 = 2.15. Ore at1.23 gives replacement total13.22. |
| Owned stock | One owned bar does not remove a shared batch and remains unused; two owned ore reduce external ore from9 to7. Cash total7×1.23+2.15=10.76. |
| Missing versus zero | Missing ore quote leaves total unknown with known material0 and fees215. Explicit ore0 gives total215. Unknown shared fee leaves total unknown with other known fees110. |
| Exclusive outcomes | Ore3 at.07, attempt fee.02, output fee.01. Probabilities .6 for normal2+dust1, .25 for normal1+rare1, .15 failure. Costs26/25/23. Normal sale cap1 at.11 with 50% tax/floor and fee.01 yields4; rare cap1 at1 with 10% tax/half_up and fee.03 yields87. Revenues4/91/0; profits-22/66/-23. Weighted revenue503/20, cost253/10, profit-3/20; downside-23, upside66, loss probability3/4. |
| Independent bonus and sale cap | A separately attested .5 chance of normal1 adds an output fee even when the normal sale cap is exhausted. Six profits: -22,-23,66,65,-23,-20; probabilities3/10,3/10,1/8,1/8,3/40,3/40. Expected revenue509/20, cost129/5 and profit-7/20. No resale credit for leftovers. |
| Unknown and unsellable | An unknown outcome probability leaves expected profit/loss probability unknown. A bound output cannot be a planned market sale. |
| Fractional FIFO | Opening ore2 basis1; buy ore3 basis701. Consume ore4: basis1+1402/3=1405/3. Add craft fee200: output basis2005/3. Allocate .3 to bar3 (basis401/2), .7 to dust2 (basis2807/6). Sell bar2 gross1000 fee100: profit2299/3. Failed dust1 consumes2807/12 plus fee1: final realized profit6377/12. Cash -701-200+1000-100-1=-2. Remaining basis: bar1=401/6, dust1=2807/12, ore1=701/3. Opening basis is not new cash. |

These cases cover `p6-mathqa`'s calculation regression requirement with existing
catalog, materials, economics, valuation, batches, routes, scenarios and ledger tests.
They do not validate the real-game inputs to those calculations.

## Recovery and input checks

`test_recovery.py` exercises populated catalog history, observations/calculations,
rollback on a restored copy, legacy catalog/plan migrations on copies only, deleted-plan
revision counters, immutable journal revisions, committed WAL data, refusal of foreign/
future/corrupt/missing sources, no-overwrite including orphaned sidecars, failure cleanup,
CLI exit codes and the distinction between SQLite integrity and payload validation.

`test_security_recovery.py` exercises corrupt plan/ledger files, simulated disk-write
failure, preserved inputs/previews, non-ASCII CSRF, invalid percent-encoded UTF-8,
duplicate form fields, malformed GET targets, Host/Origin rejection, response headers
and stalled-body timeout recovery. The timeout is an inactivity timeout, not a total
upload deadline. This is local HTTP evidence, not rendered browser or keyboard QA.

Existing `test_price_service.py`, `test_price_cache.py` and `test_market_groundwork.py`
retain synthetic provider-outage, quota, retry and freshness evidence. No real provider
is configured or contacted. The guide describes manual-mode operation during an outage.

## Release evidence matrix

| Brief section 14 criterion | Current evidence / remaining work |
| --- | --- |
| Arithmetic correctness | Synthetic regression suite plus seven hand-calculated acceptance tests pass; see TEST_RESULTS. p6-mathqa COMPLETE for that requirement. |
| Catalog identity/recipes | Synthetic contracts pass; permitted real 100-item/25-recipe pilot BLOCKED with p1-catalog. |
| Both workflows | Existing local HTTP behavior and owner acceptance retained; 20 real pilot cases BLOCKED. |
| Provenance/completeness | Library and form regressions preserve source/time/scope/unknowns; visual and real-source acceptance pending. |
| Failure/recovery | Per-file backup/restore and migrated-copy drills pass; changed-catalog JSON launch/plan compatibility drill remains Part 02 work. Production provider outage integration blocked. |
| Security/privacy | Focused source/input/storage review and regressions completed; single-user local scope. This is not a comprehensive independent security audit. |
| Installation/operations | Source-checkout instructions, retention and recovery guidance published with this checkpoint; reproducible distribution/license decision and cross-environment install acceptance pending. |
| Performance | No p95 or declared pilot-hardware performance result measured here. |
| Localization/accessibility/display | Visual/keyboard/layout QA deferred by owner; no new browser attempt. Roadmap's original content preserved. |
| Automatic-price/overlay | Gates A/B UNVERIFIED; real adapter blocked, Phase 05 deferred. These optional gates alone do not bar a manual release. |

Manual edition is **NOT RELEASED**: applicable pilot/quality evidence remains open.
No remote CI, real-market reconciliation, anti-cheat safety or production-security
approval is implied by the local tests. Phase 06 remains IN_PROGRESS.
