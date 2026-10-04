# Phase 01 — executed validation

Date: 2026-10-04. Environment: Linux, Python 3.12.14; SQLite via standard library.
No external dependencies installed. All market/catalog data used is SYNTHETIC.

## Application checks

Command: `python3 -m unittest discover -v`

Result: **47 tests passed**, zero failures/errors (0.788 seconds in the recorded run).

| Suite | Tests | Evidence |
|---|---:|---|
| Identity | 8 | Stable JSON round-trip, variant/market/currency separation, unknown scope and cross-region rejection, attribute canonicalization, strict types. |
| Catalog | 12 | Fixture import, bilingual alias search/disambiguation, orphans, duplicate identities/recipes, cycles, scope/rights, malformed/oversized input. |
| Models | 11 | Exact amounts and negative result values, invalid inputs, joint/failure outcomes, exact probability sums under low Decimal precision, trade restrictions, source time/nulls. |
| SQLite storage/migrations | 14 | Reopen, migrations 1 to 2, immutable records, foreign references, rollback, simulated write failure, stale-writer rejection, checksum verification. |
| CLI | 2 | Actual subprocess validate/import/inspect, invalid import preserves the catalog, inspecting an absent DB does not create it. |

Command: `python3 -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json`

Result: release `SYNTHETIC-demo-v1`, 7 item variants, 3 recipes; dataset kind SYNTHETIC.
The CLI integration test also executes import and inspect against temporary SQLite.
The transaction test injects a SQLite trigger failure; it does not simulate an OS crash.
The concurrency test uses two database connections with a stale expected release ID.

## Documentation and archive

The untouched recovered bootstrap passed `python3 scripts/validate_bootstrap.py`
before the baseline commit: 7 phases, 42 IDs, 14 original artifact checksums.
The validator was then updated to permit evidenced implementation completion and
check the compatible roadmap progress sidecar against the backlog. The final
checkpoint receipt records the post-change document/manifest validation outcome.
The original bilingual HTML SHA-256 remains
`0881ff82158428f87fa5ed52d47ea601d4bd5665d116a179c49b3f04d623ec87`.

## Not tested or claimed

No real catalog correctness/rights validation, authenticated price response, provider
permission, game-client behavior, overlay, UI, production calculation engine, remote
CI, GitHub upload, PR or deployment. No claim of live-price freshness. Tests run on
Linux only; Windows/macOS runtime behavior remains untested.
