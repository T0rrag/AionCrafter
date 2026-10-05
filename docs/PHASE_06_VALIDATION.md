# Phase 06 — Manual-edition validation, Parts 01–03

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
| Failure/recovery | Per-file backup/restore plus validated stored-catalog JSON export and the Part 02 changed-recipe launch/compatibility/restore drill pass. Prior plans/journals reject mismatched catalog digests without remapping; original observations, revisions and results recover from last-known-good copies. Production provider outage integration remains blocked. |
| Security/privacy | Focused source/input/storage review and regressions completed; single-user local scope. This is not a comprehensive independent security audit. |
| Installation/operations | Part 03 builds a deterministic validation-only source-checkout ZIP twice, proves byte equality, extracts it into a clean directory and validates it from a clean venv on the declared Linux CI runner. License/distribution decision and cross-environment source-install acceptance remain pending. |
| Performance | Part 03 SYNTHETIC cached-calculation benchmark: 250 warmups + 2,000 samples, p95 0.449492 ms on CPython 3.12.14 / Linux x86_64 / AMD EPYC 7763 / 4 logical CPUs. This meets the proposed <300 ms threshold for that workload only; the brief requires pilot datasets for release acceptance, which remain blocked. |
| Localization/accessibility/display | Visual/keyboard/layout QA deferred by owner; no new browser attempt. Roadmap's original content preserved. |
| Automatic-price/overlay | Gates A/B UNVERIFIED; real adapter blocked, Phase 05 deferred. These optional gates alone do not bar a manual release. |

Manual edition is **NOT RELEASED**: applicable pilot/quality evidence remains open.
Remote CI evidence exists for the explicitly identified Phase 06 implementation runs; it does
not imply real-market reconciliation, anti-cheat safety or production-security approval. Phase 06 remains IN_PROGRESS.


## Part 02 catalog-change evidence

`export-catalog` reads a recognized catalog database without migration and exports either
the active or an explicitly selected stored release to a new JSON path. Before writing it
checks the stored SHA-256, strict catalog validity and equality between the row release ID
and payload release ID; after writing it rechecks the digest. Existing destinations are
refused and partial files created by the command are removed on failure.

The end-to-end synthetic drill changes recipe requirements under a new release ID, publishes
and exports that release, starts the local web process with the changed JSON, and confirms
that a pre-change plan and journal are rejected by their existing digest contracts. Database
rows are compared before/after rejection to prove no automatic remap. Backups are restored
to new paths, the original release is exported again byte-for-byte, and the original
observation, calculation, plan revision 2, journal revision 2 and evaluated ledger result
are recovered.

GitHub Actions run 37310693174 on implementation `d01f575b2c4a88d802828820f0d1dd3f9c3f9ea7`
passed 269 tests, compileall, synthetic catalog validation and bootstrap on Python 3.12.14.
This closes the specifically planned Part 02 recovery drill, not the whole p6-patches task:
real provider health/version integration and the real pilot remain unavailable.


## Part 03 reproducible source-checkout and SYNTHETIC performance evidence

Implementation `0ad954dc2fcb5a564544fe397f81f09c7a7dc89c` adds
`scripts/build_source_checkout.py`, `scripts/benchmark_cached_calculation.py` and
`tests/test_phase06_package_performance.py`. The source builder is deliberately not a
wheel/installer/release: it creates an internal validation ZIP from the source checkout,
fixes archive metadata/order, excludes runtime caches, refuses overwrite and writes
`SOURCE_ARTIFACT.json` with `license_status=unresolved` and `public_release=false`.

GitHub Actions run 37328773165 checked out that exact SHA. Two builds were byte-identical:
SHA-256 `c03bac34b62271f5fbed3b16c488445cfc2712ba835de79b414ff52ac1718132`.
The workflow extracted the archive into a fresh directory, created a fresh virtual
environment and successfully ran synthetic catalog validation plus bootstrap from the
extracted source tree.

The performance workload is intentionally narrow and deterministic: one provider fetch
primes `PriceCache`; measured operations must then be cache hits and execute
`item_economics` for the deterministic `synthetic-bar` fixture. Environment:
GitHub Actions Linux x86_64, Linux 6.17.0-1022-azure/glibc 2.39, CPython 3.12.14,
AMD EPYC 7763 64-Core Processor, 4 logical CPUs. With 250 warmup iterations and
2,000 measured samples: p50 0.386905 ms, p95 0.449492 ms, p99 0.521868 ms,
max 0.885099 ms; exactly one provider call occurred and the proposed <300 ms p95
threshold was met.

This is **SYNTHETIC local-computation evidence**, not a pilot dataset, live provider,
browser rendering or overlay measurement. Therefore it does not close p6-golive or the
brief's pilot-dataset performance acceptance. p6-package also remains IN_PROGRESS because
the redistribution-license decision and cross-environment source-install evidence are open.
