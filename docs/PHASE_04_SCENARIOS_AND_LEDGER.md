# Phase 04 — manual scenarios, ranking and actual records

All regression evidence is **SYNTHETIC ONLY**. No game probabilities, profession rules,
provider stock, sale volumes or fee schedules are supplied or verified by this feature.
Gates A/B remain UNVERIFIED. The existing materials/item workflows remain available.

## One-attempt scenarios

In the crafting workflow choose `scenarios`, a recipe, product and planned sale cap.
Enter an assumed selling price and explicit sale fees. The probability attestation
must name the selected recipe; an all-input-consumption reference must cover failure
as well as success. Blank evidence keeps expectations/cost unknown. Catalog probability
sources remain visible. An attestation is a user assertion to audit, not app verification.
Saved plans bind the catalog digest, so changed recipe content requires explicit migration.

The engine enumerates mutually exclusive recipe outcomes. All outputs within one outcome
occur together. Sale quantities are capped separately within each scenario; unplanned
outputs are leftovers without credited revenue. Actual output-unit craft fees follow
each scenario's full output. Sale tax is rounded per item/scenario before exact rational
weighting. Failure consumes the full declared input only when supported by the evidence.
Other consumption/refund rules are unsupported and remain unknown.

`BonusOutput` is a separate library contract for Bernoulli bonuses, independent of the
exclusive outcome and each other only with explicit evidence. Conditional/correlated
bonuses must be represented as exhaustive joint outcomes instead. The form exposes
catalog outcomes; it does not provide a bonus editor or invent default probabilities.
`AttemptEvidence` binds the exact recipe and bonuses, including build and content.
The form/library reports one attempt, never a guaranteed recursive yield or the probability
of a multi-attempt target. Downside is worst modeled profit, not a market-loss guarantee.

## Market evidence and conditional rankings

Stock labels distinguish unknown from zero, vendor stock from listing stock, and asking
prices from completed-sale prices. `SalesVolume` records explicit completed units in a
closed interval with identity/provenance/time. Overlapping samples are preserved, never
summed. A completed-sale price's legacy available-quantity field is not treated as volume.
No volume or sell-through is inferred from a low asking price. Provider volume/depth is
available to library callers; automatic import/activation remains blocked by Gate A.

Choose `rank` to rank the selected target's deterministic recipe subsets. Supply an
explicit source-age limit, additional-cash budget, allowed professions and per-recipe
profession evidence/confirmed requirements. Vendor restrictions require explicit
confirmation. The UI compares up to seven candidates/128 subsets, like Part 01; it is
not a general optimizer and does not mix buying/crafting units of the same variant.

Profit and ROI charge replacement cost. Budget checks additional cash after owned stock
plus fixed sale fees. Missing fees/prices, stale/future/unknown source ages, unconfirmed
requirements, unknown/filtered professions, invalid vendor eligibility, insufficient
reported quantity, nontradeable outputs, nonpositive profit and over-budget routes are
excluded with reasons. Zero-cost ROI is undefined. Passing estimates remain conditional
on sales and source coverage; no confident liquidity recommendation is made. Ranking
recomputes freshness when a saved plan is loaded. Source observation time, not reload or
ingestion time, determines freshness. The library also accepts multiple explicit targets.

## Actual-results ledger

Open **Record actual purchases, crafts and sales** from the calculator. Create a named
journal with an explicit market/currency; optionally record the original total profit
estimate for that journal. Add opening inventory first, then purchases, actual crafts
(including failures), and completed sales in time order. Preview a record, inspect the
result, then save. Load, export and preview-import operate locally. The original estimate
does not change actual costs; the difference is partial while activity/stock remains.

The cost method is explicitly FIFO. Purchase totals include acquisition fees. Opening
stock's historical cost is basis, not new cash outflow. Crafts transfer consumed basis
plus actual craft fees into outputs. One output inherits the full basis; multiple outputs
need explicit shares summing to one or their basis remains unknown. Failure expenses the
consumed basis and craft fee. Completed sales deduct FIFO basis and actual sale fees.
Unsold stock retains its historical basis. Fractional allocations remain exact rational
amounts; no inferred market price or arbitrary rounding replaces an actual receipt.

Blank money is unknown; explicit zero is valid. Overselling/unrecorded consumption,
out-of-order events, duplicate IDs, mismatched scope/currency and malformed imports fail.
Journals use a separate SQLite file (`<plans path>.ledger.sqlite3`), immutable append-only
revisions and optimistic stale-write rejection. Export JSON preserves original IDs/times.
To correct prior records, export and create a separately named corrected journal; this
version does not implement reversals or deletion. Local retention/deletion guidance is
part of Phase 06. The UI requires CSRF for journal POST actions and escapes receipt text.

## Evidence and limits

Part 02 adds 58 tests: 14 stochastic, 8 liquidity, 14 ranking, 15 ledger, 7 HTTP form.
Ledger tests include 60 independent conservation cases with fractional costs and joint
outputs. Full suite: 238 passed on Windows/Python 3.12.14. Compileall, synthetic catalog
validation and diff checks passed. HTTP checks are not visual/keyboard QA; that remains
deferred. No real-game pilot, provider reconciliation, automatic activation or release
acceptance is claimed. The single-owner loopback application and bounded UI are groundwork,
not evidence of production-scale provider or large-catalog acceptance.
