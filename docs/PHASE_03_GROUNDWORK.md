# Phase 03 provider-independent contracts

These modules are offline groundwork. The calculator still uses its accepted manual
flows. No real provider is connected, no credentials/endpoints/quotas are invented,
and no automatic-price feature is enabled. All examples/tests are SYNTHETIC ONLY.
Gate A stays UNVERIFIED; this is not market reconciliation or release acceptance.

## Freshness

`PriceCache` owns one `PriceProvider`, captures its capabilities, and keys entries by
the complete `PriceIdentity` (catalog/build/item/variant/market/faction/currency).
Provider capabilities must remain fixed for the lifetime of the cache. It validates
scope, record types, rights, ingestion timestamps and unique immutable observation IDs
before atomically storing a response. Changed records need new IDs. Empty responses
are cached as missing and replace old listings; unavailable prices are never zero.

`PriceObservation.observed_at` remains the source time, or null for unknown age.
Its original `fetched_at` also stays intact. `CachedPrices.retrieved_at` records when
this cache received the response, including a replay. Cache hits change neither time.
TTL expiration uses retrieval age; source freshness uses observed age. Source age
strictly greater than `max_source_age` is stale; equality is fresh. TTL expires at
equality. A backward clock jump expires transport cache and flags future observations.
Both time thresholds are explicit caller choices, not verified freshness promises.

Cache/service are single-owner, in-memory foundations, not a shared production cache.
The ID registry covers both provider responses and explicit manual selections, and lasts
for that instance; persistent immutable history uses `Store`. `remember_observations`
reserves IDs atomically without creating/replacing provider cache entries. Rejected
batches reserve nothing. Identical replay is idempotent, but changes to any record field
need a new ID, including after a provider entry is replaced or retry failures are reset.
Production adapters will need a shared quota owner, bounded retention, transport timeout
and cancellation, plus authorized source/capability evidence. Do not deploy one separate
quota counter per concurrent request and assume provider-wide limits are enforced.

## Request coordination

`PriceService.resolve` returns one `PriceResolution` per distinct input identity, in
first-request order. Single-identity transport is the default. Batch transport requires
explicit `batched=True` and `BatchPriceProvider`; every requested response key must be
present (an empty tuple means missing). Incomplete/extra-key batches fail atomically.

`RequestPolicy` requires batch size, requests per fixed window, window duration, maximum
attempts, initial/capped exponential backoff and terminal-error cooldown. There are no
provider-specific defaults. Every attempted transport, successful or failed, consumes
quota. A normalized `ProviderFailure` carries retryability and optional Retry-After;
Retry-After is never shortened by the local backoff cap. Timeouts become retryable;
invalid contracts and permanent errors do not retry automatically. Unexpected adapter
programming errors propagate rather than being concealed as missing prices.

There are no sleeps or background jobs. The caller may retry at `retry_at`. Shared
cooldown blocks later batches, limiting retry storms. Maximum attempts applies across
calls, not just one resolve invocation, and is evaluated separately for each identity.
When one member of a retryable batch is exhausted, newer members retain their remaining
attempts under the same shared cooldown/quota. Permanent errors exhaust every affected
member. Exhausted identities require an explicit
`reset_failures()`, which does not reset quota or bypass cooldown. On failure, a previous
record is returned as `stale_error`; without one the state is `error`. The error code,
next allowed retry and per-observation freshness remain separate fields.

An explicit `manual={identity: observation}` chooses a MANUAL observation with matching
identity and verified/synthetic rights. Its original provenance is returned with
`origin=manual`; provider cache and error history remain intact. This selection lasts
for that call only, so callers retaining an override must pass it again. No silently
created manual price or zero fallback. Existing reference labels and storage records
can preserve/display those observations without activating an automatic provider.

## Quantity and stack semantics

`ListingOffer` wraps an existing LISTING observation, its exact total price and an
explicit partial-purchase flag. Known positive available quantity is required. Partial
purchase requires an exact unit price; when a unit price is supplied it must agree
with the whole-offer total. An indivisible stack may have only an exact total price,
avoiding rounding a nonterminating per-unit price (three units for 1.00, for example).

`depth_cost` requires declared listing-depth capability, matching identities, unique
observation IDs and one source/ingestion snapshot. The adapter must ensure this is a
coherent book, not historical repeated listings; timestamps alone do not establish
that evidence. It returns the minimum cash cost within the supplied book, with integer
currency arithmetic, exact whole-stack subset search and cheapest divisible units.
Overbuy is explicit and receives no resale credit. Equal cost prefers fewer purchased
units. `max_states` is an explicit cumulative computational work budget, not a provider
quota. Exceeding it raises SEARCH_LIMIT instead of returning a guessed optimum.

Insufficient books return a known covered subtotal, missing quantity, and `total=None`.
Covered books are labelled `stock=snapshot_only`, never guaranteed current availability.
Original observations are retained for age/provenance; stale snapshots must remain
labelled stale by the caller. This pure function performs no refresh or source selection.

`indicative_cost` multiplies a single acquisition reference/minimum price exactly but
always labels stock unverified. `purchased=0`, `missing=requested` describe unverified
coverage, not a promise of no market stock. Unknown price gives `total=None`; a known
zero gives an indicative zero. Completed sales and vendor sell-back are rejected.
Historical sales, minimums and aggregate prices cannot masquerade as listing depth.

## Evidence and remaining work

See `tests/test_price_cache.py`, `tests/test_price_service.py`,
`tests/test_acquisition.py` and `tests/test_market_groundwork.py`. Deterministic tests
inject a clock and scripted provider, including exhaustive-oracle checks of 60 small
mixed books and persistence/manual-fallback integration. They make no network calls
or sleeps. No real 20-item/two-snapshot reconciliation is claimed.

p3-freshness/resilience/depth remain IN_PROGRESS: engineering contracts are implemented,
while authorized adapter/application integration and market acceptance remain pending.
p3-adapter/reconcile/releaseprice remain BLOCKED. Preserve all 42 backlog IDs, deferred
visual QA and later real-game pilot timing. Do not begin Phase 04 in this chat.
