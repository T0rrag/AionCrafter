# Manual edition — installation, operation and recovery

This is a source-checkout engineering preview, **not a public release**. Bundled data
is SYNTHETIC ONLY, with fictional region/build/market, prices and rules. No real AION 2
client or market has been validated. No game process, live provider, overlay or account
credentials are used. Run as a normal local user; no administrator privileges are needed.
Independent project; not affiliated with NC, Overwolf or CurseForge. Repository contents
do not currently declare a redistribution license; no game-data license is granted here.
Bundled fixture attribution is in `docs/sources/SYNTHETIC.md`.

## Start from a verified checkpoint

Use Python 3.12 with its standard-library SQLite. No pip install or third-party packages
are required. Earlier suite evidence exists on Windows/Python 3.12.14. Part 03 additionally
validated a deterministic source artifact and isolated source-tree startup on GitHub Actions
Linux/CPython 3.12.14. Cross-environment source-artifact acceptance remains pending. In commands below, Windows users with the Python launcher can
replace `python` with `py -3.12`.

```text
git clone --branch phase/06-release https://github.com/T0rrag/AionCrafter.git
cd AionCrafter
git rev-parse HEAD
python -m unittest discover -q
python scripts/validate_bootstrap.py
python -m aioncrafter validate tests/fixtures/SYNTHETIC-catalog-v1.json
python -m aioncrafter.web --catalog tests/fixtures/SYNTHETIC-catalog-v1.json
```

Compare the checkout SHA to the current delivery receipt and remote head. Newer
documentation may follow its tested implementation SHA. Open `http://127.0.0.1:8765`.
Stop the terminal server with Ctrl+C before update or recovery. Do not expose the
loopback application through a proxy or use it as a multi-user public server.

For the demo select an explicit fictional market (for example `test-server`), currency
`TEST`, precision2, a faction mode and an ISO timestamp with timezone. Blank price means
unknown; enter zero only when explicitly zero. Materials mode needs quantities and
prices without a recipe. Item mode additionally needs product, recipe, target sale
quantity, sale price and explicit tax/fee/rounding assumptions. Owned inputs reduce
additional cash, not replacement value. An actual profit needs actual ledger records.
See `PHASE_04_CRAFTING.md` and `PHASE_04_SCENARIOS_AND_LEDGER.md` for recursive routes,
sale caps, conditional rankings and the separate FIFO ledger.

No automatic provider is enabled. A source outage does not refresh old observation
times or supply missing prices; enter a clearly attributed manual override only when
you have the needed evidence. Saved plans retain original source observations. Synthetic
outage/quota tests are library evidence, not a working production provider connection.

## Validation-only source artifact and performance check

For engineering verification only, the checkout can build a deterministic source ZIP:

```text
python scripts/build_source_checkout.py --output /tmp/aioncrafter-source.zip
python scripts/benchmark_cached_calculation.py --warmup 250 --samples 2000 --target-p95-ms 300
```

The ZIP is not a wheel, signed installer or public release. Its embedded
`SOURCE_ARTIFACT.json` says `license_status=unresolved` and `public_release=false`.
The builder refuses overwrite. Phase 06 Part 03 CI built two byte-identical archives,
extracted one into a fresh directory and validated it from a clean virtual environment.

The benchmark primes one SYNTHETIC provider response and then measures cached
`PriceCache` + deterministic `item_economics` operations. Run 37328773165 used 250
warmups and 2,000 samples on CPython 3.12.14 / Linux x86_64 / AMD EPYC 7763
(4 logical CPUs): p95 0.449492 ms. That is below the proposed 300 ms target for this
SYNTHETIC workload only. It is not pilot-data, live-provider, browser or overlay evidence.

## Local data and retention

| Data | Default location / behavior |
| --- | --- |
| Calculator catalog | JSON supplied by `--catalog`, loaded at startup. Retain the exact file and its attribution. |
| Plans | `local-data/plans.sqlite3`, or the exact path supplied by `--plans`. All immutable revisions remain until explicit named-plan deletion. A name/revision counter remains to reject stale tabs. |
| Actual journals | Plans path plus `.ledger.sqlite3`: default `local-data/plans.sqlite3.ledger.sqlite3`. Append-only revisions; no per-journal delete or automatic expiry in this version. |
| Catalog store | Optional CLI `--database` path. Catalog releases, observations and calculations are retained; rollback changes only the active catalog pointer. |
| Exports/backups | User-selected paths, without encryption or automatic expiry. JSON/CSV can contain market choices, timestamps, prices, inventory and receipt references. |

Reset clears unsaved inputs only. Delete a saved plan through its confirmed UI action;
it does not delete journals, exports or backups. To retire all local history, stop the
server and close every SQLite client, confirm the exact paths, then remove the selected
databases and their matching sidecars plus any exports/backups you intend to discard.
Do not remove individual WAL/journal files from an active database. File/row deletion
is not a secure-erasure guarantee. Keep personal receipt details and tokens out of notes.

The manual server has no configured telemetry or outbound provider transport. Standard
HTTP access logs go to its terminal and include the request target; do not put secrets
in URLs. Local files use your account's filesystem permissions and are not encrypted.
Host/Origin/CSRF guards and escaped forms are not protection from another process that
already controls your account. SQLite files and sidecars are ignored by Git; arbitrary
export filenames outside `local-data`/`private-data` still require care before staging.

## Backup before updating

Stop all application and database writers. Record the application commit, catalog JSON
SHA-256 and database paths. Keep the exact catalog JSON with the matching backup set.
Create a private backup directory, then run only commands for files that actually exist:

```text
python -m aioncrafter check-database --database local-data/plans.sqlite3
python -m aioncrafter backup --database local-data/plans.sqlite3 --output local-data/backups/plans-before-update.sqlite3
python -m aioncrafter backup --database local-data/plans.sqlite3.ledger.sqlite3 --output local-data/backups/ledger-before-update.sqlite3
```

Use the same command separately for an optional catalog database. Backups never overwrite
an existing file and refuse destinations with SQLite sidecars. Choose fresh names for
each checkpoint. The receipt prints kind, schema, integrity, bytes and SHA-256; save it
beside the backup and compare that digest again before recovery. Each snapshot is
consistent for one SQLite file, including committed WAL data; it is not an atomic snapshot
of several databases. Do not let another process use the new destination while copying.

`check-database` opens read-only without migrating schemas. SQLite may create coordination
sidecars for WAL access. It checks recognized structure, SQLite integrity and foreign keys,
not JSON payload semantics, game correctness or data rights. A structurally sound backup
can preserve an already bad application record; normal load/validation is still required.
An interrupted backup is not accepted without a successful receipt and recovery check.

## Update and recover without overwriting working data

After backing up, update to a reviewed exact application checkpoint, run its tests and
manifest validator, then start it with the intended catalog JSON. Current catalog schema2,
plan schema2 and ledger schema1 are separate stores. Opening a supported older catalog
or plan copy migrates it; a newer unsupported schema is refused. Keep pre-update backups
for an older application version; never lower schema numbers by hand.

To recover, stop writers and copy the chosen backups into NEW working paths:

```text
python -m aioncrafter backup --database local-data/backups/plans-before-update.sqlite3 --output local-data/restored-plans.sqlite3
python -m aioncrafter backup --database local-data/backups/ledger-before-update.sqlite3 --output local-data/restored-plans.sqlite3.ledger.sqlite3
python -m aioncrafter.web --catalog tests/fixtures/SYNTHETIC-catalog-v1.json --plans local-data/restored-plans.sqlite3
```

The catalog shown is the synthetic example: use the exact prior permitted JSON for your
backup set. Load a named plan and journal; verify the expected revision, observations,
times and totals. Keep the original files until recovery is accepted. Plan/journal digest
checks intentionally reject a different catalog; no automatic remapping is performed.
The paired ledger filename must derive from the restored plans path as shown above.

For a catalog database, `rollback RELEASE_ID --database PATH --expect-active CURRENT_ID`
selects a previously stored validated release without deleting later history. It does
**not** change a running web process or its `--catalog` JSON. Export the exact stored
release to a NEW file, then restart with matching plan/journal files:

```text
python -m aioncrafter export-catalog --database local-data/catalog.sqlite3 --release-id RELEASE_ID --output local-data/catalog-release.json
python -m aioncrafter.web --catalog local-data/catalog-release.json --plans local-data/restored-plans.sqlite3
```

Omit `--release-id` to export the active stored release. Export validates the catalog
database, stored checksum, strict payload and release identity and refuses to overwrite an
existing output. It preserves the exact stored JSON bytes so saved plan/journal digests can
be checked against the same catalog content. A Part 02 synthetic drill verifies that a
changed recipe release causes old plans/journals to fail compatibility checks without
rewriting them, and that restoring the prior catalog plus database backups to new paths
recovers the prior revisions and results. No automatic remapping is performed.

On `STORAGE_UNAVAILABLE`, preserve the unsaved form or journal preview, inspect the path,
free space and permissions, and check/restore a copy. A failed response does not prove a
write was never committed; reload the saved revision before retrying. Never reset or
delete a database merely to dismiss the error. A stalled upload is closed after inactivity
so the local server can handle another request; this is not public-service DoS protection.

## Release remains pending

The current edition has no real-client support claim, signed desktop package, measured
pilot-dataset p95, visual/keyboard acceptance or real-game pilot. Part 03 measured only
the declared SYNTHETIC cached-calculation workload and does not satisfy pilot acceptance. See `PHASE_06_VALIDATION.md` for
the evidence matrix, `TEST_RESULTS.md` for executed checks, and `NEXT_CHAT_PROMPT.md` for
the current continuation. Optional Gates A/B remain UNVERIFIED. The manual edition can
eventually release without them only after its own applicable quality criteria pass.
