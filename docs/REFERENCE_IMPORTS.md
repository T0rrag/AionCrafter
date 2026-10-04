# Offline reference imports — Phase 02

Select a market, currency and default observation time. Paste a JSON array of full
version-1 PriceObservation records into Approved offline references and preview.
`tests/fixtures/SYNTHETIC-price-references-v1.json` is a synthetic example for
`test-server`, TEST (2 decimals), synthetic-demo; it is not game data.

Imports accept manual observations, vendor purchase prices and aggregate snapshots.
Every item/build/variant, market/faction and currency must match exactly. Duplicate
items/observation IDs, unverified rights, sell-back and completed-sale acquisition
references are rejected. A source marked permitted must carry its permission reference;
this records the supplied claim, not an independent legal verification. Import only
sources actually approved for your use. No network provider or live access is added.

Preview merges supplied variants and retains other form observations. Save to persist
source/type/rights, observation/ingestion times and stock fields. JSON/CSV plan transfers
retain these records. Editing a reference price or time creates a linked manual
observation; unchanged records retain their IDs and times. Blank per-item timestamps
use the explicit default for manual entry. Imported unknown snapshot/vendor observation
times stay unknown until explicitly replaced. Age uses observation time, never ingestion.
Snapshots are delayed references; displayed age does not imply a verified freshness SLA.

Stock and vendor restrictions remain manual checks. These unit-reference estimates do
not enforce listing depth or vendor availability. Historical cost views still exclude
actual craft/sale fees and realized profit. Direct ingredients only; recursive work is
Phase 04. Gates A/B remain UNVERIFIED.
