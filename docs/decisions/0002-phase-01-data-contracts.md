# ADR 0002 — Phase 01 data contracts and local persistence

Date: 2026-10-04
Status: Implemented engineering proposal; pending architectural review
Tasks: p1-identity, p1-recipe, p1-trade, p1-validate, p1-storage

## Decisions

Use a small Python 3.12 standard-library package (`aioncrafter/`) and `unittest`.
No third-party package installation, service, UI or provider connection is needed
for this phase. The proposed services/packages layout can be introduced when
application boundaries require it; a monorepo scaffold adds no value yet.

Frozen dataclasses and a strict JSON codec define version-1 contracts. Import
requires all fields, including explicit nulls, and rejects unknown/duplicate fields,
coercions, booleans as integers and non-finite numbers. Catalog imports are bounded
to 8 MiB. Monetary amounts are decimal strings with declared currency precision;
fees/prices must be nonnegative, while stored result amounts can represent losses.
Probability sums use scaled integers so Decimal's ambient precision cannot hide
an invalid sum. This phase does not implement an economics engine or fee rounding.

## Identities and unknowns

Item identity includes catalog namespace, dataset kind, region, client build, source
item ID and sale variant. Variant attributes are sorted by key, and duplicate keys
are invalid. Other IDs preserve case and Unicode exactly. Price identity adds
market kind (server/group), market ID, faction applicability and currency identity
including precision. Structured canonical JSON keys avoid delimiter collisions.
Aliases, source attribution and release IDs do not form item/price identity.

Nullable quality/enhancement and unknown tradability are valid catalog metadata,
but block price identity. Unknown market region/currency/faction similarly blocks
pricing. `not_applicable` faction is an explicit choice, distinct from `unknown`.
The synthetic dataset kind prevents joining fixtures to a real market.
The selected real catalog must enumerate all additional sale-relevant attributes;
the generic contract alone cannot establish that a provider supplied all of them.

Search is scoped to build/region and language, with case/accent/spacing normalization.
Cross-item alias collisions in one language are rejected on import. Variants of the
same base item may share names; resolving such a name requires an explicit choice.

## Recipes and observations

Each outcome holds joint outputs, quantities and probability with evidence. An empty
output tuple models failure. Null probability stays unknown; no equal distribution
is inferred. All-known exhaustive outcomes sum exactly to one. Null fees/requirements
mean unknown; empty arrays explicitly mean none. Requirements and acquisition
restrictions are descriptive at this stage, not evaluated game rules.

Price observations distinguish manual, vendor purchase/sell-back, listing, minimum,
snapshot and completed-sale semantics. Source time may be null; ingestion time is
separate and never resets source age. Missing price/stock remain null. Overrides
append observations and reference the original, retaining its amount and provenance.
No observation-selection policy, freshness TTL, depth pricing or live adapter is
implemented. Vendor sell-back and completed-sale references are not purchase quotes.

## Persistence and review

SQLite schema 1 stores immutable catalog releases and one active pointer; migration
2 adds immutable observations/calculations. Typed JSON payloads preserve complete
contracts, with relational release references and a price-identity index.
Publication validates the whole catalog before a transaction and requires the
expected previous active release to prevent stale writers. It returns an item/recipe
diff. Rollback switches to a previously validated, checksum-verified release without
deleting history. Snapshots retain prior catalog and observation IDs.

Catalog rights status is a recorded declaration plus an evidence reference, not an
automatic legal verification. Import rejects `unverified` rights. Actual source
rights and recipe correctness still require review before real data is admitted.

## Boundaries

Gate A and Gate B remain UNVERIFIED. The real pilot and catalog are unresolved.
Seven fixture variants and three recipes do not satisfy p1-catalog's real-data target
of 100 items / 25 verified recipes. Calculation records are storage contracts only.
No Phase 02 calculator UI, calculation service or game integration has been built.
