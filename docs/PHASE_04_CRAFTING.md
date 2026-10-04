# Phase 04 crafting contracts — Part 01

All fixtures are fictional SYNTHETIC data; none establishes game rules.

`plan_batches` accepts explicit selected deterministic recipes and requested quantities.
Unselected intermediates become external requirements. The dependency walk aggregates
all consumers before rounding each producer's batch count. Joint outputs use the
maximum batches needed for any output; surplus is retained, never sold implicitly.
Production is consumed before owned stock where coproducts make stock unnecessary.
Each identity obeys produced + owned used + external = required + leftover.
Execution order puts dependencies first. Catalog cycles and unknown stochastic yields
fail explicitly; competing output producers require separate routes.

`price_plan` uses existing reference/depth acquisition contracts for exact quantities.
It includes fees for every executed recipe, multiplying per-output fees by all produced
units and per-attempt/batch fees by craft count. Unknown prices or fees leave total
unknown while preserving known subtotals. Whole-stack surplus is in acquisition records,
separate from crafted surplus. Sources retain exact variant, market, provenance/time.

`compare_routes` enumerates selected recipe subsets under an explicit budget. It does
not mix buying/crafting units of the same variant or execute competing producers
together. Its lowest-known cost is conditional, not a global optimum or recommendation.
Additional cash deducts usable inventory; replacement cost ignores inventory. Recipe
requirements are reported, not verified. Manual/vendor estimates do not prove stock
or vendor eligibility. Existing observation contracts reject bound market listings.

Choose `crafting` in the local calculator, select product/target recipe and quantity,
then explicitly select intermediates and objective. Selected mode expands that route;
compare mode evaluates up to seven candidates (128 subsets). Target fee override applies
only to the target recipe. Other recipe fees must be recorded or remain unknown.
Saved plans retain these choices and observation provenance. Historical consumed-cost
fields are not applied to recursive estimates; no realized-profit claim is made.

Remaining: stochastic outcomes and downside, explicit eligibility filtering, liquidity,
ranking, optional actual-transaction ledger and broader acceptance. Browser visual QA
is deferred. No provider requests or automatic-price activation were added.
