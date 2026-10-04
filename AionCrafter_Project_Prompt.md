# AionCrafter — Complete Project and Implementation Prompt

**Brief version:** 1.3 · **Prepared:** 4 October 2026  
**Companion artifact:** `AionCrafter_Roadmap.html` v1.1, with an English/Spanish toggle (unchanged by this revision).  
**Workflow revision:** phase-scoped chats and handoffs (section 20), architectural control and GitHub delivery by phase (section 21).  
**Research baseline:** the investigation recorded in the existing roadmap on 4 October 2026. This Markdown consolidates that record; it is not a new authenticated API test or a new verification of provider terms. Recheck changeable facts before committing to an integration.

---

## 1. Your role and assignment

Act as the product-minded software architect and implementation engineer for **AionCrafter**, an external **AION 2 crafting-economics companion** inspired by **Auctionator**, the World of Warcraft addon.

Treat this entire document as the authoritative project brief, but use focused retrieval rather than pasting or reproducing it in every chat. Follow the phase-scoped chat protocol in sections 20–21: work on the current phase, save a handoff, and stop at its boundary. Build a maintainable application incrementally, not just a visual mockup or another feasibility essay. Keep the economics engine, item/recipe catalog, market-price providers and presentation layers separate. Make the first useful release work with the user's own observed prices, while investigating permitted automatic market data and optional overlay support independently.

Inspect any existing repository and supplied artifacts before making changes. Preserve existing working behavior and user data. Distinguish confirmed requirements, engineering proposals, provider statements and unverified assumptions. Do not silently promote a proposal or marketing claim to a verified fact.

The HTML roadmap is a planning artifact, not an implemented application. No application repository, production service, authenticated market integration or approved overlay has been established by that artifact. The initially checked task, `p0-audit`, records the earlier public-source review only. A checked box is not proof that an external release gate has passed.

## 2. Confirmed user intent

The user wants two workflows:

**Workflow A — Item economics.** Given a crafted object, show the materials needed to make it, their market unit prices and total cost; show a suitable price reference for the finished product; calculate the potential benefit/profit or loss.

**Workflow B — Materials-only price checker.** When the game already supplies the recipe, accept the required materials and quantities and provide their prices and acquisition total. Do not make this workflow depend on identifying a recipe or entering the finished-product price.

Auction-house prices are preferred where usable, but other suitable price references are acceptable when their origin and limitations are explicit.

A WoW-style in-game addon is **not required**. An external application, including an overlay, is acceptable. The user suggested “surgeforge” or Overwolf. The roadmap interprets “surgeforge” as a likely reference to **CurseForge**, because Auctionator was the linked reference; that interpretation is not a confirmed new platform requirement. Evaluate **Overwolf** as an optional overlay route rather than assuming CurseForge provides an AION 2 addon runtime. [S08, S14]

The user also requested a standalone HTML project roadmap, then an **English/Spanish toggle in that roadmap** and this complete Markdown prompt. English/Spanish support in the eventual application is a sensible proposed default, not a separately confirmed requirement for the game client or its data source.

## 3. Product boundaries and working principles

Build a decision tool, not an automated player. Exclude automatic buying, listing, crafting and other game-command automation. Do not add custom client/DLL injection, memory reading, packet capture or collection of game-account credentials as data-acquisition shortcuts.

An overlay is a way to display information. It is not a market-price source. A working overlay does not establish that auction data is available, and a working price adapter does not establish that an overlay is supported.

Do not assume a game region from the player's physical location. Select a single pilot region, server or market group, relevant faction, client build and language explicitly. Taiwan was mentioned as a candidate in planning, not a fixed requirement. Do not mix Global, KR and TW datasets solely because localized item names resemble one another.

Do not claim universal taxes, fees, craft yields, proc probabilities, item counts, tradability rules or server coverage without evidence for the chosen market and build. Earlier fictional examples, including an EU server identifier and a 25% proc example, are not verified AION 2 facts.

Use synthetic fixtures, clearly labeled, to build the engine before permitted real data is available. Do not present invented items, recipe mappings or sample prices as a live game catalog.

## 4. Market-data investigation: inherited evidence and limits

### 4.1 Official NC / PLAYNC route — not established for AION 2

The earlier review located NC's developer portal and market documentation for **Lineage 2M**, including `/market/items/{item_id}/price`. It did **not** verify a documented AION 2 auction-price endpoint. The existence of an NC developer portal does not prove that every NC game exposes the same data. [S01, S02]

Do not implement a guessed AION 2 route. In particular, `GET /market/items/{item_id}?server=EU-01` was an earlier illustrative shape, not an endpoint discovered or tested. A working Lineage 2M endpoint cannot be treated as cross-game access.

Next evidence required: ask NC for AION 2-specific documentation, permitted use, supported regions, authentication, price semantics, update behavior, quotas and distribution rights.

### 4.2 Aion2t.com — concrete community-provider lead

The provider page recorded in the roadmap described collected auction-price snapshots: free registered accounts receive observations aged **20–30 hours**, while Premium receives the latest collected snapshot. The reviewed page did not establish a fixed freshness guarantee. This is a provider statement, not proof that AionCrafter has an authorized working integration. No authenticated item-price response was obtained in that audit. [S03]

The recorded terms restrict scraping, copying and redistribution without permission. Recheck the current text and request suitable access rights rather than building against internal or authenticated website routes without authorization. Website membership or a consumer Premium subscription is not automatically an API/data license. [S04]

Request a small permitted sample before committing engineering work to a provider adapter. Verify region/server/faction coverage, stable item and variant IDs, listing versus completed-sale semantics, quantity/depth fields, source timestamps, update cadence, API quotas, cost and caching/display/redistribution rights. A public contact route is listed in the source register; the roadmap's inquiry is a draft and has **not** been sent. [S15]

### 4.3 Recipe and calculator references — not live-price API evidence

**Aion2.app:** the recorded crafting-page text described entering ingredient auction prices manually and identified the game client as its recipe-data source. A general “official API” footer does not establish an auction-price API. [S05]

**AION2 Hub:** the recorded calculator demonstrated recursive material requirements and distinguished Global from KR/TW recipe datasets. Treat it as evidence of recipe-calculator feasibility and a possible catalog reference, not a confirmed reusable price feed. Public access does not establish reuse rights. [S06]

**Grachy / aion2-craft:** the inspected README listed auction-house price integration among future plans. A README is not an API contract and can lag behind a deployed service. Do not infer either a working endpoint or its definite absence from that text. [S07]

### 4.4 Overwolf — separate support and data questions

The recorded framework documentation described HTML/JavaScript applications, overlay windows and independent desktop windows. Overwolf's game-event interfaces are game-specific. The reviewed GEP index did not establish AION 2-specific auction events or an auction-data interface. [S08, S10, S11]

AION 2 rendering compatibility for the exact regional executable and chosen framework remained unresolved. The support directory's dynamic results were insufficient in the earlier audit. “Unverified” is not the same as “definitely unsupported.” Check the appropriate Native, Electron and, where relevant, OOPO support entries. [S09, S13]

The Native onboarding page recorded in the roadmap described proposal/whitelisting, public-app and monetization requirements and said private apps were not approved. Recheck the current framework-specific requirements before making Overwolf mandatory. Evaluate whether they fit this project's intended audience and distribution model. [S12]

### 4.5 Limits of the earlier audit

The roadmap records a public-documentation review, not an authenticated integration test. It obtained no authenticated auction response, item-level market quote or comparison with the actual in-game market. Direct HTTP requests from that earlier execution environment failed DNS resolution, and JavaScript-only directories were not fully inspectable with the available reader. No game-client network traffic was inspected.

Those limitations do not establish that an API is absent. Conversely, they do not support a claim that an API is already available to this project. No third-party account was created, no subscription purchased, no provider inquiry sent and no game session examined by the roadmap work.

**Disposition:** proceed with manual/reference-price calculations; investigate a permitted community snapshot/API; keep automatic fresh AH data and Overwolf compatibility unresolved until their independent gates pass.

## 5. Independent go/no-go gates

### Gate A — Authorized automatic price data

Pass this gate only when all of the following are evidenced:

1. Documented access and permission appropriate to this app, caching, display and intended distribution.
2. A working sample with item/variant identity, market scope, currency, price semantics and source observation time—or explicit unknowns that meet the intended feature's quality requirements.
3. Measured freshness and coverage, reconciled against the same in-game market and variants.
4. Permitted request limits, sustainable cost and a defined outage/staleness policy.

Pilot validation target: at least **20 representative items**, including materials, intermediates and finished products, at **two observation times**. Record observations and discrepancies rather than merely testing that a request returns HTTP 200.

Passing Gate A enables only the markets and capabilities actually verified. Failure or delay does not block the manual/reference edition. A recent ingestion time must not turn an old snapshot into a “live” quote.

### Gate B — Supported overlay platform

Pass this gate only after confirming the exact AION 2 regional executable and chosen framework, resolving platform approval and game-compliance requirements, and testing visibility, hotkeys, focus/interaction, DPI scaling and declared display modes in the real game.

Keep pricing, recipes and calculations independent of the overlay shell. Test 1080p/1440p, multiple monitors, hotkey collisions, other overlays and measurable resource/frame-time impact on declared hardware. Do not claim universal compatibility or guaranteed anti-cheat safety without the appropriate evidence.

Passing Gate B enables a specifically supported overlay edition. Otherwise retain the browser or normal desktop edition. An always-on-top desktop window is a separate fallback to test in windowed/borderless mode; do not promise exclusive-fullscreen support without tests. [S08–S13]

## 6. Functional behavior

### 6.1 Item economics

Provide item search with disambiguation by region/build and sale-relevant variant. Select the recipe and target quantity. Show direct ingredients first, with optional recursive expansion into raw materials and intermediate components.

For each input show the required quantity, chosen acquisition method, unit-price reference, subtotal, inventory adjustment where applicable, and source/market/age. Show the finished-product selling-price reference, supported sell quantity, crafting and selling fees, total cost, net proceeds, estimated profit/loss, return on cost and break-even selling price when defined.

For an already-owned crafted item, explain that the result estimates replacement economics. It does not reconstruct actual historical profit. Historical accounting requires user-recorded costs, crafting outcomes, sale proceeds and fees.

Display unknown, incomplete, stale, unsellable and insufficient-stock states as first-class outcomes, not as exceptional UI failures hidden behind a profitable green number.

### 6.2 Materials-only price checker

Accept selected catalog items or a pasted list of names and quantities. Resolve ambiguous localized names interactively; never silently choose the first match. Reuse the selected market, or require one before pricing.

Return ingredient quantities, unit prices, subtotals, additional quantities to acquire and a shopping total. Do not require a recipe ID, output item or selling-price field. Missing quotes must not become zero. A partial subtotal is allowed only when clearly labeled with the missing materials and unknown total.

### 6.3 Saved work and optional later features

Persist material lists, favorites, calculation plans, market settings, manually entered prices and user-supplied inventory quantities. Provide validated JSON/CSV import/export, useful error messages, and an explicit reset.

Later phases can add recursive buy-versus-craft comparisons, batch-aware leftovers, verified probabilistic outcomes, rankings of adequately priced crafts, price history from permitted observations and a user-maintained actual-cost ledger. Only display market volume or completed-sale information if the source supplies it; do not manufacture liquidity estimates from minimum asking prices.

Screenshot import is a future, optional, user-triggered extension. Prefer local processing, explicit confidence checks and user confirmation of item, scope, quantity and price. It creates a dated observation, not an automatic all-market feed. Do not make OCR or screenshot ingestion an MVP dependency.

## 7. Price identity, provenance and completeness

Use stable item IDs plus catalog region/build and sale-relevant variants such as quality, enhancement and tradability. Localized names are search aliases, not primary keys. Quotes must also match market scope, relevant server/faction and currency.

Keep **source observation time** and **ingestion/fetch time** separate. An unknown source time means freshness is unknown; a cache hit must not reset the observation's age. Retain provider attribution and the selected price's origin even when a user overrides it manually.

Distinguish a manual observation, vendor purchase reference, vendor sell-back reference, current listing, minimum listing, aggregate snapshot and completed sale. Do not use a vendor sell-back price as the cost of buying a material. Do not silently add incompatible currencies or bound and unbound variants.

Where data permits, calculate the cost of buying the entire requested quantity from listing depth and actual stack rules. One cheap unit does not price an unlimited shopping basket. With only a minimum/reference quote, label the total **indicative** and available stock **unverified**. Do not extrapolate missing quantity depth without a visible qualification.

Use a configurable, documented provider freshness policy based on measured behavior. Do not invent a universal cache duration and call it real time. Show missing-item counts and reject wrong-region or wrong-variant joins rather than silently substituting another market.

Preferred source order is a documented NC feed **if confirmed**, then a licensed community API/snapshot, then user observations, permitted imports and applicable vendor references. This is a policy proposal, not evidence that those automated integrations currently exist.

## 8. Calculation engine specification

### 8.1 Deterministic batches

For a simple single-output deterministic recipe:

```text
craft_count = ceil(target_units / units_per_craft)
produced_units = craft_count × units_per_craft
leftover_units = produced_units − planned_sell_units

craft_cost = Σ acquisition_cost(required_inputs) + total_crafting_fees
net_proceeds = planned_sell_units × selling_unit_price × (1 − sale_tax_rate)
               − listing_and_other_sale_fees
estimated_profit = net_proceeds − craft_cost
ROI_percent = estimated_profit / craft_cost × 100
```

Do not assume all produced units will sell. Define the accounting treatment for unsold leftovers and report it. Distinguish recipe fee per attempt, per batch and per unit; verify the actual fee and rounding rules for the selected market.

For a single output, a fixed cost, positive planned sell quantity and tax strictly below 100%:

```text
break_even_unit_price =
  (craft_cost + listing_and_other_sale_fees)
  / (planned_sell_units × (1 − sale_tax_rate))
```

If fees depend on price, minimums, tiers or market-specific rounding, solve using those verified rules instead of applying the simplified formula blindly. ROI is undefined at zero cost. Break-even is undefined where its denominator is zero. Reject invalid quantities, negative prices, non-finite numbers and invalid probability/tax ranges.

Production money arithmetic must use Python `Decimal` or validated integer monetary units, not binary floating-point arithmetic. Encode exact amounts as strings in JSON. Use explicit rounding consistent with verified market rules. The HTML's illustrative calculator is a demonstration of the specification, not the production economics engine.

### 8.2 Inventory and actual cost

Separate three concepts:

- **Additional cash required:** what the player must spend now after usable inventory is deducted.
- **Economic/replacement cost:** a consistent valuation of the resources consumed, including owned materials.
- **Actual historical cost/profit:** the player's recorded transactions and realized outcomes.

Owned materials are not automatically economically free. Any user-selected zero valuation must be explicit rather than silently treating missing prices as zero. Avoid double-counting inventory or shared inputs across recipe branches.

### 8.3 Recursive recipes and buy-versus-craft

Validate the recipe graph and detect cycles. Aggregate shared material demand appropriately before final batch rounding, track yields and carry leftovers. Respect craft requirements, bound inputs, vendor restrictions, currencies and market stock.

For an intermediate component, compare buying the required amount with crafting the required batches, including fees and leftover treatment. Define the optimization objective: minimum additional cash, minimum economic cost or another explicit objective. A simple per-node heuristic is not necessarily globally optimal when inputs, leftovers or stock are shared; label its limitations rather than promising a mathematical optimum without demonstrating one.

### 8.4 Stochastic recipes

For mutually exclusive outcomes with verified probabilities:

```text
expected_profit_per_attempt =
  Σ (outcome_probability × net_outcome_value)
  − expected_cost_per_attempt
```

Probabilities must sum to one for an exclusive-outcome model. Bonus outputs require a separate model. Account for failure costs and materials consumed where verified. Unknown probabilities remain unknown; do not hardcode a universal 25% proc chance or replace uncertain outputs with guaranteed yields.

Report expected revenue/profit and downside scenarios separately from deterministic results. A positive expected value is not a guaranteed return for one attempt.

### 8.5 Synthetic regression example

This is **fictional**, in generic currency, with one produced and sold unit. It is not an AION 2 recipe, fee schedule or live price:

| Input/result | Value |
|---|---:|
| Materials | 9,300 |
| Crafting fee | 500 |
| Total craft cost | 9,800 |
| Selling price | 14,500 |
| Illustrative sale tax | 10% |
| Other sale fees | 0 |
| Net proceeds | 13,050 |
| Estimated profit | +3,250 |
| ROI | 33.163265…%, displayed as 33.2% |
| Simplified break-even unit price | 10,888.888… before applying verified rounding |

## 9. Proposed architecture and contracts

Use a thin presentation layer with a shared backend economics engine and replaceable data adapters:

```text
Browser / desktop UI                 Optional approved overlay
             \                            /
              \--- shared application contracts ---/
                                |
                  Application API + economics engine
                                |
           +--------------------+--------------------+
           |                    |                    |
     Catalog provider      Price providers         Storage
     versioned recipes     manual / vendor         observations
     stable item IDs       official / partner      plans / history
                           only when approved      provenance
```

The game client is not a backend dependency. Keep provider credentials on the backend, never in a browser or overlay bundle.

**Proposed stack, not a locked technology mandate:** React + TypeScript + Vite for the UI; Python + FastAPI for application endpoints and pure economics functions; SQLite with migrations initially; PostgreSQL only when actual usage warrants it. An approved Overwolf Native/Electron shell is conditional. A conventional desktop wrapper can be evaluated separately. Containerize backend deployment when useful; do not create infrastructure complexity before the MVP needs it.

Verify current official documentation and choose compatible, pinned dependency versions at implementation time. Do not invent available SDK features or reuse outdated onboarding assumptions.

### 9.1 Suggested repository layout

```text
apps/
  web/                       # full browser UI
  overlay/                   # optional shell, gated by platform support
services/
  api/                       # application API and provider adapters
  api/economics/             # pure calculation functions; no network calls
packages/
  contracts/                 # versioned DTOs and request/response models
data/
  catalog/                   # permitted, region/build-versioned imports
tests/
  fixtures/                  # synthetic and approved samples
  economics/                 # deterministic and stochastic regression tests
  integration/               # scope, provider, import and quota tests
docs/
  decisions/                 # architecture decisions and evidence
  sources/                   # source metadata and data-rights records
```

This is a proposed structure, not an existing repository.

### 9.2 Minimum entities

| Entity | Required meaning |
|---|---|
| `Item` | Stable identity, catalog/build scope, localized aliases, variant and tradability information. |
| `Recipe` | Input quantities, yield, crafting fees/requirements, possible outputs and probability provenance. |
| `MarketScope` | Explicit region, market group/server, relevant faction and currency. |
| `PriceObservation` | Item/variant, market, source, price semantics, exact amount, quantity support and timestamps. |
| `Calculation` | Selected inputs/recipes, price observations used, assumptions, costs, results and completeness. |
| `Inventory` / `Ledger` | Optional user-supplied holdings and transactions; never inferred from game memory. |

### 9.3 Observation contract example

This is an illustrative **AionCrafter-owned schema**, not an NC or community-provider response:

```json
{
  "item_id": "catalog-id",
  "variant_key": "quality/enhancement/tradability",
  "region": "chosen-region",
  "market_scope": "server-or-world-group",
  "faction": null,
  "server_id": "chosen-server",
  "currency": "declared-currency",
  "unit_price": "1250",
  "available_quantity": null,
  "price_type": "manual_observation",
  "observed_at": null,
  "fetched_at": "2026-10-04T00:00:00Z",
  "provider": "manual",
  "catalog_version": "selected-build"
}
```

The timestamp is synthetic. Production timestamps must be timezone-aware. Source time can remain null for imported legacy data, but that makes its freshness unknown; new manual observations should request a date/time from the user. Do not substitute ingestion time for missing source time. Evolve the contract explicitly to include currency precision, permitted listing-depth data, provider license attribution and capabilities as needed.

### 9.4 Provider interfaces and application endpoints

Define `CatalogProvider` separately from `PriceProvider`. Manual, vendor-reference and authorized automated adapters must normalize into common contracts. Expose provider capabilities explicitly: scope coverage, listing depth, completed-sale support, observation timestamps and update behavior. Do not implement “official” adapters against speculative endpoints.

Suggested **internal AionCrafter endpoints**, subject to design review:

```text
GET  /api/v1/items
GET  /api/v1/recipes/{recipe_id}
POST /api/v1/prices/resolve
POST /api/v1/prices/manual
POST /api/v1/calculations/item
POST /api/v1/calculations/materials
GET  /api/v1/providers/status
```

These routes are for our application only. None is a claim about an external game API. Use typed validation, versioned schemas, structured missing-data errors, cancellation/timeouts, allowed batching and bounded retries. Pure calculations must not perform network calls.

## 10. Presentation, localization and the existing roadmap

For the application, propose an item-economics screen, materials-only screen, source-aware price editor, saved plans/settings and a later compact overlay view. Keep source, scope, age and incompleteness visible in both full and compact views. Never make a stale or incomplete result look confidently profitable through color alone.

The existing roadmap is a self-contained HTML file with embedded CSS/JavaScript, ten navigation sections, seven phases, 42 task checkboxes, two external gates, searchable/filterable tasks, collapsible phase panels, a fictional calculator, editable project notes, import/export, theme controls, print layout, a decision register and 15 sources.

Preserve these features when editing it. Its v1.1 language control switches between **EN** and **ES** without replacing the application DOM or resetting user input. Translate headings, prose, task descriptions, source descriptions, tooltips, accessibility labels, placeholders, validation messages, confirmations, notifications and calculator number formatting. Keep source URLs, task IDs, executable code/schema identifiers and user-authored notes unchanged.

Search must work with English and Spanish task vocabulary regardless of the selected UI language, with case- and accent-insensitive matching. Persist the preferred language when browser storage is available. Update `html.lang`, active/pressed state and an accessible language-change announcement. Switching language must preserve notes, task completion, inputs, filter/search state and expanded panels. Maintain usable desktop/mobile layouts, keyboard access and reduced-motion behavior.

Keep the roadmap's storage key `aioncrafter-roadmap-v1` and compatible progress schema. A v1.1 export contains:

```json
{
  "project": "AionCrafter",
  "schemaVersion": 1,
  "roadmapVersion": "1.1",
  "researchDate": "2026-10-04",
  "exportedAt": "2026-10-04T00:00:00.000Z",
  "completed": ["p0-audit"],
  "notes": "",
  "theme": "dark",
  "language": "en"
}
```

The export timestamp above is illustrative. Accept valid older exports without a `language` field while retaining the current language preference. Validate task IDs, notes and schema; reject unknown IDs, malformed JSON and unsupported languages. The current roadmap limits imported progress files to 256 KiB and notes to 50,000 characters. Do not silently delete notes during localization. Reset clears notes/progress after confirmation but retains theme and language preferences. Show a clear export fallback when local storage is unavailable.

The standalone HTML does not query a game/API or need a CDN/account. Static English content remains readable without JavaScript; language switching and interactive behavior require JavaScript. External reference links naturally need a connection. The demo calculator's edits are not promised as persistent project data; notes, checklist progress, theme and language are the saved roadmap state.

For the eventual app, carry English/Spanish localization forward as a proposed default and keep canonical item identifiers independent from UI language and game-language aliases.

## 11. Execution strategy and dependency order

Resume the current phase from the latest verified checkpoint. When no checkpoint exists, begin with a Phase 00 kickoff: record the existing evidence, resolve the pilot decisions that can be resolved and identify external blockers. Work toward Phase 01 and Phase 02 using a small permitted catalog or clearly synthetic fixtures and the player's observations, in separate phase-scoped chats. Unresolved external price/overlay inquiries may remain open while independent calculator work proceeds; do not mark those inquiries or gates complete. Record any decision to proceed around a blocker in the checkpoint. Section 20 governs chat transitions; work is performed only in active sessions, not asynchronously.

```text
Phase 00: evidence and scope
       ↓
Phase 01: data foundation
       ↓
Phase 02: manual-first calculator — first usable release
       ├── Phase 03: automatic price adapter, only after Gate A
       ├── Phase 04: crafting intelligence; manual prices are sufficient initially
       └── Phase 05: overlay packaging, only after Gate B
       ↓
Phase 06: tested, appropriately labeled release and maintenance
```

Milestones are not promised calendar dates. The three extensions need not block one another or the manual release. Keep a short evidence/decision log and report what is implemented, tested, deferred and externally blocked after each increment.

## 12. Security, data rights and operational requirements

Keep provider secrets server-side and out of logs, exported user plans and the overlay bundle. Minimize personal data. Validate imported files and all API input; never evaluate imported content as code. Define local data retention/deletion and an explicit reset. Do not collect game-account credentials to compensate for a missing price integration.

For external data, record source, version, rights, attribution and permission constraints. Public availability is not itself a redistribution license. Do not create accounts, buy subscriptions, send partner messages or publish a public app merely because those actions appear in the roadmap; obtain the necessary owner authorization.

Use versioned catalog releases, migrations, import validation and rollback to a last known-good dataset. Respect provider request quotas, backoff on throttling, prevent retry storms and expose degraded/stale/error states. Document supported clients, markets and display modes rather than promising universal coverage. Sign packaged desktop releases when applicable and include a non-affiliation notice.

## 13. Complete implementation backlog — 7 phases, 42 tasks

Priorities: **P0** = correctness or release-critical; **P1** = usability; **P2** = enhancement. Stable task IDs match the HTML roadmap. Only the inherited public-source record is initially marked complete; do not mark implementation or external validation complete without performing it.

### Phase 00 — Resolve the data & platform gates

**Dependency:** No prerequisite.  
**Outcome:** A documented go / conditional-go decision. No assumed API.

- [x] **`p0-audit` · P0 · Record the public-source investigation**  
  Completed for this document: distinguish official documentation, provider claims, unverified integration and missing evidence. This is not an authenticated API test.

- [ ] **`p0-scope` · P0 · Lock a single pilot market**  
  Choose region, server or market group, faction where relevant, client build and language. TW is a candidate, not a fixed requirement. Never infer the game region from the player’s location.

- [ ] **`p0-official` · P0 · Ask NC about an AION 2 market-data interface**  
  Request documentation, supported regions, authentication, permitted use, refresh frequency and limits. Do not reuse Lineage 2M endpoints as if they belonged to AION 2.

- [ ] **`p0-partner` · P0 · Request a price-data partnership**  
  Ask Aion2t about programmatic access, source methodology, timestamps, market coverage, rates, cost, storage and redistribution rights. A consumer Premium account is not the same as an API/data licence.

- [ ] **`p0-sample` · P0 · Validate a representative price sample**  
  Obtain at least 20 items at two observation times, including raw materials, intermediates and finished goods. Compare with the same in-game market and item variant. Log gaps, delays and discrepancies.

- [ ] **`p0-platform` · P0 · Confirm the overlay route**  
  Check the exact AION 2 regional client in Overwolf’s Native / Electron support directory and test it. Clarify app approval and publishing requirements; keep a normal desktop-window route independent.


### Phase 01 — Build the data foundation

**Dependency:** Pilot scope + permitted catalog source.  
**Outcome:** Versioned recipes and stable item identities, independent of any price provider.

- [ ] **`p1-identity` · P0 · Define item and market identities**  
  Use stable item IDs plus region/build, quality, enhancement and other sale-relevant variants. Price keys must also include market scope and source currency. Localized names are search aliases, not primary keys.

- [ ] **`p1-catalog` · P0 · Obtain and import a permitted catalog**  
  Pilot target: at least 100 relevant items and 25 verified recipes. Confirm rights for data, icons and redistribution; a public repository or webpage alone is not a reuse licence.

- [ ] **`p1-recipe` · P0 · Model complete crafting outcomes**  
  Store inputs, quantities, batch yield, crafting fee, requirements and possible outputs. Attach source/build metadata; leave unknown probabilities explicitly unknown.

- [ ] **`p1-trade` · P0 · Model tradability and acquisition constraints**  
  Represent bound/unbound variants, vendor restrictions, quantity limits and currency types. A vendor sell-back value is not an auction purchase price; incompatible currencies are not silently added.

- [ ] **`p1-validate` · P0 · Validate imports before publishing**  
  Reject orphan IDs, impossible quantities, duplicate identities, cycles and ambiguous aliases. Review changes after each patch and preserve the last known-good catalog.

- [ ] **`p1-storage` · P0 · Create storage and provider contracts**  
  Start with SQLite and migrations. Define Item, Recipe, MarketScope, PriceObservation and Calculation records. Use exact arithmetic for money and explicit nulls for missing prices.


### Phase 02 — Ship the manual-first calculator

**Dependency:** Phase 01; does not require live prices.  
**Outcome:** Both requested workflows work, with honest manual/reference-price labels.

- [ ] **`p2-itemflow` · P0 · Implement item → materials → margin**  
  Search a product, select its recipe and quantity, show direct ingredients or a fully expanded tree, price the output and calculate estimated profit/loss.

- [ ] **`p2-listflow` · P0 · Implement materials-only pricing**  
  Accept selected items or a pasted materials list. Resolve ambiguous names with a picker. Return unit prices, quantities, subtotals and a total without requiring a recipe or a selling-price field.

- [ ] **`p2-editor` · P0 · Add a source-aware price editor**  
  Let users enter their own observed prices or approved reference imports. Require market and observation time; distinguish manual, vendor, snapshot, delayed and unavailable values.

- [ ] **`p2-costmodes` · P0 · Separate cash needed from economic cost**  
  Owned materials reduce the shopping list, not automatically the economic cost. Offer replacement-cost valuation, additional cash required and actual historical cost when the user supplies a ledger.

- [ ] **`p2-economics` · P0 · Implement fees, yield and missing-price states**  
  Calculate batch cost, net sale proceeds, profit, ROI and break-even price. Tax and fees are configurable and unverified until checked for the selected market. Never treat missing prices as zero.

- [ ] **`p2-save` · P1 · Save plans and material lists**  
  Persist favorites, market settings, user-entered prices and inventory quantities. Add JSON/CSV import/export with validation and a clear reset. No trading or crafting automation.


### Phase 03 — Connect permitted market prices

**Dependency:** Gate A + Phase 01; plugs into Phase 02.  
**Outcome:** Automatic price observations with provenance, coverage and explicit age.

- [ ] **`p3-adapter` · P0 · Implement the approved provider adapter**  
  Only after permission and a working sample: add an official or contracted community adapter behind the same interface as manual prices. Keep credentials on the backend.

- [ ] **`p3-freshness` · P0 · Preserve observation time and cache age**  
  Record source-observed time, fetch time, price type and scope separately. A cache refresh must never make an old observation appear new. Unknown source time means freshness unknown.

- [ ] **`p3-resilience` · P0 · Respect quotas and degrade predictably**  
  Batch permitted requests, use provider limits, backoff on throttling and stop retry storms. Show stale/error states and allow manual overrides without silently hiding their origin.

- [ ] **`p3-depth` · P0 · Use prices suitable for the requested quantity**  
  When supported, consume listing depth or whole-stack offers to calculate the cost of buying all required units. With only a reference/minimum price, label the total indicative and stock unverified.

- [ ] **`p3-reconcile` · P0 · Run market reconciliation tests**  
  Check 20 representative items across two snapshots, multiple variants and scope changes. Test wrong-region joins, zero listings, partial coverage and listed-versus-sold price distinctions.

- [ ] **`p3-releaseprice` · P0 · Approve the automatic-price feature**  
  Enable it only for validated markets. Display age, source and missing-item count on every result. Do not describe snapshots as real time without evidence of their update behavior.


### Phase 04 — Add crafting intelligence

**Dependency:** Phase 02; Phase 03 for automatic market intelligence.  
**Outcome:** Batch-aware buy/craft decisions and risk-aware estimates.

- [ ] **`p4-batches` · P0 · Handle recursive yields and leftovers**  
  Round craft counts upward by output yield, merge shared ingredients, carry leftovers and detect recipe cycles. Treat expected stochastic yields differently from guaranteed outputs.

- [ ] **`p4-buycraft` · P1 · Compare buying against crafting**  
  Evaluate intermediate components at the requested quantity, including batch fees and leftovers. Respect recipe requirements, bound inputs and available market stock.

- [ ] **`p4-proc` · P0 · Model success, failure and proc outcomes**  
  Use verified probabilities per recipe/build; distinguish alternative outputs from bonus outputs. Report expected revenue and downside scenarios instead of promising a guaranteed return.

- [ ] **`p4-liquidity` · P1 · Show market uncertainty**  
  Keep asking prices separate from completed sales. Display stock and volume only when the provider supplies them. Do not infer liquidity or sell-through from a single cheap listing.

- [ ] **`p4-rank` · P1 · Rank crafts by usable economics**  
  Filter by profession, budget, tradability and price completeness. Show estimated profit, capital required, ROI and data age; exclude incomplete or stale results from confident recommendations.

- [ ] **`p4-ledger` · P2 · Compare estimates with actual outcomes**  
  Optionally record user-entered purchase costs, crafting results, sale proceeds and fees. A finished item alone cannot reveal the player’s historical profit.


### Phase 05 — Package the companion overlay

**Dependency:** Gate B + Phase 02; independent of Gate A.  
**Outcome:** A compact in-game view or an explicitly supported desktop companion.

- [ ] **`p5-shell` · P0 · Select and validate the production shell**  
  Choose an approved Overwolf Native/Electron route after support checks. Keep the calculator reusable in a browser or standard desktop window when platform support is absent.

- [ ] **`p5-compact` · P1 · Build the compact companion view**  
  Reuse item search, a pinned material list and margin summary. Keep market, source and age visible even in compact mode. Avoid covering essential game controls.

- [ ] **`p5-hotkeys` · P0 · Add deliberate focus and visibility controls**  
  Provide a configurable show/hide hotkey, clear close control and a visible interaction mode. Test focus restoration; do not send automated commands to the game.

- [ ] **`p5-fallback` · P1 · Validate the desktop-window fallback**  
  Test an always-on-top window with borderless/windowed mode; do not claim exclusive-fullscreen compatibility without tests. The browser/second-screen mode remains available.

- [ ] **`p5-privacy` · P0 · Keep the default integration minimal**  
  No custom DLL injection, memory reading, packet capture, credential collection or automated trading. Optional screenshot import is a later, user-triggered feature—not an MVP dependency.

- [ ] **`p5-display` · P0 · Test supported display and performance setups**  
  Check 1080p/1440p, DPI scaling, multiple monitors, hotkey collisions and coexistence with other overlays. Record idle CPU, memory and frame-time impact on declared hardware.


### Phase 06 — Validate, release & maintain

**Dependency:** Phase 02 + quality gate; 03/05 only for included features.  
**Outcome:** A release whose claims match the data and platform actually tested.

- [ ] **`p6-mathqa` · P0 · Pass the calculation regression suite**  
  Cover multi-output recipes, batch rounding, shared ingredients, fees, missing/zero values, unknown proc rates and non-tradable outputs. Verify exact monetary rounding.

- [ ] **`p6-usertest` · P0 · Complete both workflows with pilot users**  
  Use 20 real cases in one declared market. Verify materials, quantity, source age, listing interpretation and fee assumptions against the game; document unresolved discrepancies.

- [ ] **`p6-patches` · P0 · Make patch and outage handling recoverable**  
  Version recipes, provider schemas and pricing rules. Add migration tests, provider health reporting and rollback to the last known-good data release.

- [ ] **`p6-security` · P0 · Review secrets, privacy and input handling**  
  Keep provider credentials server-side; minimize collected data. Validate imported files and API input, restrict desktop privileges and document retention/deletion behavior.

- [ ] **`p6-package` · P1 · Publish installation and operating guidance**  
  Include supported clients/markets, update procedure, known limitations, data attribution, licensing and non-affiliation notice. Sign desktop releases when applicable.

- [ ] **`p6-golive` · P0 · Run the release checklist and label the edition**  
  Manual edition can ship without Gate A. Automatic-price and Overwolf editions require their respective gates plus quality checks. Archive the evidence supporting each public claim.

## 14. Acceptance and release criteria

These are proposed targets, not claims of completed tests. Keep each edition clearly labeled. The manual edition can release without Gate A or B; automatic prices require Gate A, and an Overwolf edition requires Gate B. All included features still require their applicable quality checks.

### Catalog identity and recipes

100 pilot items and 25 recipes checked; no unresolved item IDs, cycles or cross-region joins. Dataset rights recorded.

### Both requested workflows

20 real pilot scenarios complete from input to result. Materials-only mode does not require recipe data or an output price.

### Arithmetic correctness

Known test fixtures match hand-calculated totals; tests cover batch rounding, fees, shared ingredients, missing values, unknown proc rates and unsellable outputs.

### Price provenance and completeness

Every price displays source, market and age—or “unknown.” Missing data never becomes zero. Quantities unsupported by listing depth are flagged as indicative.

### Automatic-price edition

Gate A passed; 20 representative items reconciled at two source times. The UI uses measured freshness, not a claim of guaranteed real time.

### Overlay edition

Gate B passed for declared clients and display modes; hotkeys, focus restoration, closing behavior and coexistence tested. No “anti-cheat safe” guarantee without appropriate evidence.

### Failure and recovery

Provider outage, quota limits, corrupt imports and recipe changes produce clear states. A last known-good catalog can be restored.

### Performance target

Cached, deterministic calculations respond within 300 ms at the 95th percentile on declared test hardware and pilot datasets. Overlay resource impact is measured and documented separately.

### Additional localization and state-regression checks

Verify EN → ES → EN without losing task states, notes, calculator input, search/filter selections or expanded phase panels. Verify translated number formatting, errors, confirmations, themes and accessibility labels. Confirm bilingual accent-insensitive search, validated export/import, compatibility with v1 exports, graceful storage failure, reset behavior and print-state restoration. Check narrow and wide layouts for unintended page-level horizontal overflow.

Keep synthetic unit tests separate from live/provider integration checks. A local mock or fixture is not a successful market-data test. Record the test environment and disclose any untested game-client or platform behavior.

## 15. Inherited decision register

These statuses describe the roadmap baseline. Reconfirm changeable platform statements before adopting them.

### D-01 — No WoW-style in-game addon

**Status:** User decision. Use an external companion; an overlay is acceptable. Do not make an AION 2 addon environment a requirement.

### D-02 — Core engine independent of market provider

**Status:** Proposed. Manual and approved automated sources share one observation contract. A provider failure should not invalidate the whole application.

### D-03 — Do not promise live prices yet

**Status:** Open evidence. Keep Gate A unresolved until there is authorized access, a usable sample and measured freshness. A marketing claim is not an integration test.

### D-04 — Overwolf is conditional, not mandatory

**Status:** Open evidence. The current Native onboarding page requires proposal/whitelisting and describes public-app and monetization conditions; it says private apps are not approved. Review this fit before adopting the platform. [S12]

### D-05 — Single-market pilot before broader coverage

**Status:** To decide. Region, server/market group, faction and build must be selected explicitly. Do not mix Taiwan, Korea or Global data because item names look alike.

### D-06 — Safety and data rights are release conditions

**Status:** Proposed. Prefer a documented publisher feed or a contracted provider. Keep custom packet capture, memory reading, client injection and game automation outside this project’s scope.

## 16. Partner inquiry draft — not sent

**Subject:** AionCrafter — permitted AION 2 auction-price integration

Hello, I’m building AionCrafter, an external crafting-cost and profit calculator for AION 2. I’m evaluating authorized market-price providers. Do you offer API access or a data partnership for your auction snapshots?

I would need to confirm regional/server/faction coverage; stable item and variant IDs; price type (listing, minimum, aggregate or completed sale); available quantities; source observation timestamps and cadence; authentication, quotas and pricing; how data is collected; and permission to cache, display and redistribute derived calculations in a web app and optional overlay.

A small sample for 20 materials/intermediates/finished items at two observation times would let us validate the integration. I will not assume that website membership grants API or redistribution rights. Thank you.

Do not send this draft without the owner's authorization. Record any response as evidence; an inquiry sent is not permission granted.

## 17. Source register — retained from the 4 October 2026 roadmap

These links preserve the original investigation trail. Their inclusion is not a new review of current availability, terms, app compatibility or API behavior. Reopen relevant primary documentation before making time-sensitive implementation claims. Provider pages substantiate what a provider states, not an authenticated end-to-end integration.

### S01 — NC / PLAYNC Developers · Official developer portal

The indexed portal describes Lineage 2M item and market-price APIs. It does not establish an AION 2 auction API.

Source: <https://developers.plaync.com/>

### S02 — NC / Lineage 2M API · Official market-price documentation

The documented /market/items/{item_id}/price route is under the Lineage 2M API. Wrong game for this integration.

Source: <https://developers.plaync.com/apis/l2m/price>

### S03 — Aion2t.com · Provider’s Premium / access page

Provider-stated price availability and snapshot ages; no authenticated price response was obtained for this audit.

Source: <https://aion2t.com/premium>

### S04 — Aion2t.com · Provider’s terms of service

Section 3 restricts scraping, copying and redistribution without permission. Updated 26 April 2026.

Source: <https://aion2t.com/terms>

### S05 — Aion2.app · Crafting calculator

Describes entering ingredient auction prices and says recipe data comes from the game client. Its API footer is not proof of an auction feed.

Source: <https://aion2.app/crafting>

### S06 — AION2 Hub · Crafting calculator and dataset scope

Demonstrates recursive recipes and separates Global from KR/TW datasets; availability does not establish reuse rights.

Source: <https://aion2hub.com/tools/crafting-calculator>

### S07 — Grachy / GitHub · Author’s crafting project README

The inspected README still lists auction-house price integration as a future plan. It is not an API contract or a reliable statement about the live site’s current backend.

Source: <https://github.com/Grachy/aion2-craft>

### S08 — Overwolf · Official framework overview

Documents HTML/JavaScript apps, overlay windows and independent desktop windows.

Source: <https://dev.overwolf.com/ow-native/getting-started/overview/>

### S09 — Overwolf · Official game-support directory

Check Native, Electron and OOPO support for the actual regional executable. Its dynamic results were not sufficient to confirm AION 2 support in this audit.

Source: <https://www.overwolf.com/supported-games/>

### S10 — Overwolf · Game Events Provider overview

Game events and game-info fields are explicitly game-specific; an overlay does not automatically expose auction listings.

Source: <https://dev.overwolf.com/ow-native/live-game-data-gep/live-game-data-gep-intro/>

### S11 — Overwolf · Official supported GEP documentation index

No AION 2-specific GEP documentation appeared in the inspected index. This is not proof that rendering an overlay is unsupported.

Source: <https://dev.overwolf.com/ow-native/live-game-data-gep/supported-games/game-events-sample-app/>

### S12 — Overwolf · Official app onboarding and approval

Includes proposal/whitelisting, game compliance and public-app publishing requirements. Platform commitment remains conditional.

Source: <https://dev.overwolf.com/ow-native/getting-started/project-roadmap/>

### S13 — Overwolf Support · General issues and platform requirements

States that overlay support depends on the supported game list and that the platform supports Windows.

Source: <https://support.overwolf.com/support/solutions/articles/9000177155-general-issues-and-solutions>

### S14 — CurseForge / Auctionator · Product reference

Reference for reagent-cost and profit workflows, not a source of AION 2 game data or an AION 2 addon runtime.

Source: <https://www.curseforge.com/wow/addons/auctionator>

### S15 — Aion2t.com · Provider contact

Public contact form and account-support route for partnership questions. No request has been sent.

Source: <https://aion2t.com/contact>

## 18. Open decisions to resolve before broad rollout

Record the exact pilot market and build; the catalog source and reuse rights; the supported item variants and currencies; the verified fee/tradability rules; and whether any provider can supply a usable, permitted sample with the necessary timestamp and scope fields.

For the overlay, record the target operating system and executable, platform/framework compatibility, intended private versus public distribution, approval requirements and whether the owner's publishing/monetization preferences fit the selected route. Do not force Overwolf if a normal browser or desktop edition satisfies the user's immediate needs.

For product scope, confirm whether the proposed English/Spanish application UI, inventory valuation modes, later craft ranking and ledger features are wanted in the first application release or subsequent increments. None should delay an agreed materials-only and item-economics vertical slice.

Resolve genuinely blocking questions, but do not ask for information the repository, supplied files or authorized data already provides. Where a question only blocks a later integration, proceed with clearly labeled fixtures or manual inputs and leave that integration's gate open.

## 19. Your first implementation increment and expected handoff

Start by inspecting the latest checkpoint, relevant project files and actual repository state. Do not assume the proposed repository already exists. State the current phase and translate its scope into a short implementation plan tied to the stable task IDs. Implement the smallest complete increment within that phase. Do not combine Phase 01 and Phase 02 into one chat merely to reach the first usable release; apply section 20.

Across Phase 01 and Phase 02, the first usable release should contain versioned item/recipe fixtures, explicit market identities, a pure tested calculation engine, manual price entry, both user workflows, clear provenance/missing-data states and local saved plans. Deliver only the selected phase's portion in the current chat, with an explicit checkpoint for the remainder. Use permitted real data only when rights and identity matching are established. Keep automatic providers and overlay packaging behind documented, unsatisfied gates until the relevant evidence is obtained.

Provide working files, installation/run instructions, test commands and executed test results. State which observations are synthetic, which external services are connected, which game/client tests were actually performed and which features remain conditional. Do not claim that anything was deployed, sent, purchased, approved or tested without doing it.

Update the bilingual roadmap only for work actually completed. Preserve its 42 stable task IDs and compatible progress data; add a separate documented extension to the backlog rather than silently repurposing existing IDs. Keep the source register and decision log current with dated evidence.

**Success means:** the player can reliably price a materials list or estimate a craft's economics now, while the application remains ready for an authorized market adapter and an approved overlay later. Do not let unresolved live-data access prevent a useful, honest calculator from being built.

## 20. Phase-scoped chats and context-efficient handoffs

### 20.1 Working rule and practical limit

Use **one development phase per chat inside the same existing ChatGPT project**. This is a development workflow, not an AionCrafter application feature. Do not create a separate ChatGPT project for each phase. Resume the actual current phase, rather than restarting Phase 00 in every conversation.

At a phase boundary, prepare a compact, self-contained handoff and a ready-to-paste prompt for the next chat, then stop. **Opening the new chat is the user's action by default.** A prompt alone does not create, rename or switch conversations. Never claim such an action was completed without an available, authorized tool and a verified result. Do not promise background development or automatic future continuation.

Chat separation is intended to keep active discussion focused and avoid repeatedly reproducing large histories. It is **not zero-token work or a guarantee of reduced total token usage**. ChatGPT project chats can use project instructions, files and other project chats, depending on settings. Do not rely on memory alone to preserve exact development state. [W01]

### 20.2 Starting a phase chat

Use this suggested title: `AionCrafter | Phase XX | Short phase name | Part 01`. It is a proposed title, not evidence the conversation has been renamed.

Read the current user request, this protocol, the latest project checkpoint and the previous handoff first. Retrieve the brief's relevant phase tasks, shared requirements and only the code/tests needed for the current increment. Do not repeatedly paste the whole master prompt, repository, source register or prior conversation.

Verify the available repository/archive, branch and commit when applicable. Report missing access or mismatched artifacts; never invent a repository, commit, attachment or a successful test. If a project file is missing from the new chat, use available Project/file/repository tools first and request only genuinely unavailable material.

State the active phase, its goal, task IDs, dependencies and exit criteria. Respect Phase 00–06 and the existing 42 task IDs; do not rename phases to M1–M7 or confuse phase prefixes with P0/P1/P2 priorities. The current user instruction may change scope explicitly; record such changes rather than silently rewriting requirements.

### 20.3 Checkpoint and continuation files

Maintain these files in the working repository when it exists. Without a writable repository, provide equivalent downloadable Markdown files and identify the current code archive separately. Do not claim they were saved as Project sources or committed unless that actually happened.

| File | Purpose |
|---|---|
| `docs/PROJECT_STATE.md` | Compact current state: active phase, phase/task statuses, gate states, latest artifact or commit, blockers and next eligible action. |
| `docs/handoffs/phase-XX-part-NN.md` | Dated record of this phase session's changes, decisions, actual tests and remaining work. |
| `docs/NEXT_CHAT_PROMPT.md` | Short starter for the next eligible phase, or the next part of the same phase. |

Use statuses `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE` and `DEFERRED`. `DEFERRED` or `BLOCKED` does not mean completed. Record Gate A and Gate B separately as `UNVERIFIED`, `BLOCKED` or `PASSED`, with evidence references.

The checkpoint should link to exact artifacts rather than reproducing them. Preserve previous handoffs; replace only the current-state file and next-chat starter with their latest versions. Record the checkpoint date, brief version and available code version. The actual files and executed tests must support every completion claim.

### 20.4 Phase closure and exceptions

When the phase's applicable exit criteria pass, update its task statuses and roadmap evidence, prepare the three checkpoint files, and give the user the proposed next-chat title and starter. **Do not begin the next development phase in the same chat.**

If only part of a phase is complete, report it as such. A long phase may use several chats, for example `Phase 02 | Part 01` and `Phase 02 | Part 02`; a new chat is not required after every response or individual task. Split at a coherent checkpoint when discussion becomes unwieldy, rather than asserting a precise remaining token budget without telemetry.

If externally blocked, finish any independent in-scope work, document the blocker and produce a handoff. Select the next eligible phase rather than blindly incrementing the number. Gate A controls automatic-price integration and Gate B controls the supported overlay; an unresolved gate must not force the manual calculator to stall or be marked passed. Phase 06 may release the manual edition while optional integrations remain deferred, under the release rules in section 14.

Seven phases therefore do not guarantee exactly seven chats. Reopening a phase, splitting a large phase, or pausing for external access may require more. Never call a phase complete merely because its chat is ending.

### 20.5 Compact handoff template

Aim for roughly 300–600 words, with links or file references for detail. Shorten it when little changed; include more only when necessary to avoid losing critical state. Do not include secrets or full logs.

```markdown
# AionCrafter — Phase XX / Part NN handoff
Date: <actual date>
Brief version: 1.3
Phase status: <IN_PROGRESS / BLOCKED / COMPLETE / DEFERRED>
Code: <repository + branch + verified commit, or exact archive; otherwise not created>

## Delivered and verified
<Stable task IDs, changes and supporting files; separate implemented from tested.>

## Tests actually run
<Exact commands, outcomes and essential failures; explicitly list tests not run.>

## Decisions and constraints
<Relevant accepted decisions, source/build scope, synthetic data labels.>

## Remaining work and gate status
<Unfinished task IDs, blockers, Gate A/B status and evidence references.>

## Next session
<Next eligible phase or same-phase continuation, why, first task and exit criteria.>

## Files the next chat must read
<Latest project state, this handoff, selected brief sections and relevant code/tests.>
```

### 20.6 Next-chat starter and shared project instructions

Generate a filled-in starter, not an empty template, at each checkpoint. Keep it around 150–200 words or less where practical. Name the exact next phase and first task. Include brief version, available code reference, relevant handoff and unresolved gates. If code or a repository does not exist, say so.

Example structure—not a claim that a phase has been completed:

```text
Continue AionCrafter inside this same project.
Current phase: <XX — name>; part <NN>.
Use AionCrafter_Project_Prompt.md v1.3, especially sections 20–21 and this phase's tasks.
Read <latest PROJECT_STATE.md> and <exact previous handoff> first.
Verify <repository/branch/commit or code archive> before editing.
First task: <stable ID and intended result>.
Constraints/blockers: <actual open items; Gate A/B remain unverified unless evidenced>.
Work only within this phase. Verify changes with the relevant tests.
At phase completion or a coherent pause, update the checkpoint and generate the next-chat
starter, then stop. Do not assume a new chat was created or that files were persisted.
```

For consistent use across phase chats, the user can add this compact rule to the existing project's instructions; this document does not change those settings automatically. Project instructions apply within that project. [W01]

```text
For AionCrafter development, use one phase per chat. Follow section 20 of the latest
AionCrafter_Project_Prompt.md. Start from PROJECT_STATE.md and the latest handoff;
verify the actual code and task status. Retrieve only relevant brief sections and files.
Do not rely on memory alone or repeat the full history. At a phase boundary or coherent
pause, save a compact checkpoint, test results and the next-chat starter, then stop.
The user opens the next chat in this project. Do not claim automatic chat creation,
background work, unperformed tests, passed gates or zero-token savings. Keep unfinished
phases unfinished; use a same-phase continuation or the next eligible phase as appropriate.
```

### 20.7 Workflow reference and revision scope

**W01 — OpenAI, Projects in ChatGPT.** Official documentation checked on 4 October 2026. Supports project instructions, shared project files, user-created project chats and cross-chat project context subject to settings. It does not establish an automatic phase-chat creation capability or any token-savings guarantee.

Source: <https://help.openai.com/en/articles/10169521-projects-in-chatgpt>

**v1.2 changes:** added the phase-chat protocol and aligned sections 1, 11 and 19 so the first usable release does not imply implementing multiple phases in one chat. The seven phases, 42 task IDs, two external gates, calculation requirements and S01–S15 research register remain unchanged. The HTML roadmap and its saved progress were not modified by this revision. No application code, checkpoint files, new chats or integration results are asserted to exist merely because their templates appear here.

## 21. Architectural control and phase-based GitHub delivery

### 21.1 Control chat versus development chats

The user has designated the existing conversation **`Aioncrafter - Architectural control`**. Its responsibilities are scope, architecture decisions, dependencies, evidence review and acceptance of phase deliverables. Record approved decisions in `docs/decisions/` rather than relying on chat memory. Keep implementation in separate phase-scoped chats in the **same existing ChatGPT project**. The current project is Aion2; do not create a different project for every phase.

The title above is the user's requested title. It is not a claim that ChatGPT's visible conversation title has been changed. Likewise, a prepared starter is not a created chat. Only report UI actions after an authorized tool has actually performed and verified them.

The next eligible implementation session is **`AionCrafter | Phase 01 | Data foundation | Part 01`**, starting with `p1-identity`. Use an explicitly synthetic market/build/catalog for engineering fixtures until a pilot game market and permitted real catalog are established. Phase 00 remains incomplete: this scheduling choice does not pass either external gate or complete the real-catalog task. Work only on Phase 01's foundation; do not implement the Phase 02 user interface in that chat without an explicit scope change.

### 21.2 Repository identity and current access evidence

**Intended repository:** `T0rrag/AionCrafter`. The connected GitHub login `T0rrag` was verified on 4 October 2026. No AionCrafter repository appeared in the accessible owner repository listing. The connected toolset exposes file, branch, commit, issue and PR operations but no repository-creation operation. The available browser profile has no recorded signed-in GitHub or ChatGPT session, and this runtime has no GitHub CLI login. These are capabilities of that particular execution session, not permanent limits of GitHub or ChatGPT.

The architecture bootstrap has been prepared locally. **No GitHub repository, remote branch, remote commit, issue, pull request or release is claimed to exist.** Recheck the intended repository in the next session; the user may have created it or changed access meanwhile. Do not upload to an unrelated existing repository as a workaround.

Default to a **private** new repository unless the user selects another visibility. Repository creation is the outstanding setup action; initializing it with a README gives the connector an existing branch/commit from which to work. Do not ask the user to paste passwords or tokens into chat.

### 21.3 Branches, checkpoints and review

Use one repository and one evolving codebase, not separate repositories or duplicated source trees per phase. Proposed branch names:

| Work | Branch |
|---|---|
| Reviewed baseline | `main` (or the verified existing default branch) |
| Architecture/documentation bootstrap | `phase/00-architecture-bootstrap` |
| Phase 01 | `phase/01-data-foundation` |
| Phase 02 | `phase/02-manual-calculator` |
| Phase 03 | `phase/03-market-prices` |
| Phase 04 | `phase/04-crafting-intelligence` |
| Phase 05 | `phase/05-overlay` |
| Phase 06 | `phase/06-release` |

These names are conventions, not created branches. Read the actual default branch, current commit and existing phase branch before writing. Create a missing branch from the reviewed baseline; resume an existing phase branch rather than replacing it. Independent or stacked branches must declare their base dependencies explicitly.

At each coherent checkpoint, run the applicable tests, update the project state and handoff, then commit and push that phase's changes when GitHub is available and the changes are ready. The user's request to upload by phases authorizes these project-related commits and uploads; it does not mean future work is scheduled or running in the background.

Use commit messages such as `feat(phase-01): define item and market identity contracts` and include stable task IDs in the body. Open a draft PR when a reviewable partial increment exists. Mark the phase PR ready only after its applicable exit criteria are verified. Keep it unmerged pending architectural/owner review unless merge authorization has been explicitly given. Never force-push or overwrite concurrent work to make a checkpoint fit.

A new chat/part is not a new phase. Continue on the same phase branch and PR where appropriate. A phase boundary, upload or passing test does not itself close unresolved tasks or external gates.

### 21.4 Required delivery receipt

After a remote write, read back the branch/commit or PR. Include the repository, branch, exact verified commit SHA, task IDs, commands actually run, results, remaining blockers, PR URL when present and the next-chat starter. Distinguish local preparation, remote publication, PR creation, merge and release as separate states.

Use `docs/GITHUB_DELIVERY.md` for the publishing procedure and `docs/PROJECT_STATE.md` plus `docs/backlog.json` for the recorded state. Keep the 42 task IDs and their meaning unchanged. GitHub milestones/phase issues may be created when an authorized tool supports them; until then the backlog file is a local plan, not evidence of GitHub milestones.

Do not commit secrets, `.env` files, personal correspondence, unrelated files, unlicensed game data, private provider samples or screenshots without appropriate permission. Do not change repository visibility, permissions, billing, protected-branch rules or deployment settings merely to upload code. A written review convention is not configured branch protection.

### 21.5 Compact shared instruction

```text
Reserve “Aioncrafter - Architectural control” for decisions and reviews. Implement in
separate phase chats inside the same existing project. Follow sections 20–21 of the
latest master prompt. Resume from PROJECT_STATE.md, backlog.json and the latest handoff.
Use T0rrag/AionCrafter only after verifying it exists and is accessible. Deliver each
phase on its own branch and PR; commit tested checkpoints, verify every upload, and
report its SHA. Leave merges for architectural/owner approval. Do not claim automatic
chat creation, passed gates, completed phases, uploads or tests without evidence.
```

**v1.3 changes:** adds the architectural-control role, intended GitHub repository, per-phase branches/PRs, verified-delivery receipts and a filled Phase 01 starter. No application implementation or external integration is asserted to exist. The seven phases, 42 tasks, two gates and bilingual HTML remain unchanged. The generated bootstrap is local and not yet published.
