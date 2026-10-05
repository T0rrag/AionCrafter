# ADR 0010 — Manual-edition recovery and validation

Date: 2026-10-05. Status: Implemented Phase 06 Part 01 engineering decision.
Tasks: p6-mathqa, p6-patches, p6-security, p6-package.

Continue the independent Phase 06 scope selected by ADR 0008 and the immutable
phase-04-to-phase-06 continuation. This chat owns phase/06-release from verified
main e90c295b38245e57cf53a017d96885a770ed399f. One repository writer; supporting
reviews are read-only. This increment neither reopens older phases nor releases an edition.

Use independent, hand-calculated synthetic acceptance cases alongside existing
regressions. Their results establish arithmetic behavior only. No fixture supplies
verified game prices, probabilities, fees, source rights or pilot evidence.

Database recovery uses read-only inspection and SQLite's snapshot API to a NEW path.
Recognize supported catalog/plan/ledger schemas, check SQLite integrity and foreign keys,
normalize the destination to DELETE journal mode, and report its SHA-256 after close.
Reject existing destinations and orphaned sidecars. Never automatically replace the
working database. Snapshots are per file; stop writers before backing up a related set.
Read-only WAL access can create SQLite coordination sidecars. Structural checks and
backup hashes do not validate typed payloads, catalog rights or application compatibility.
Load restored records through their normal application contracts before accepting recovery.

Catalog stores now use application_id 0x41494331. Existing untagged version-1/2 catalogs
are accepted only with the expected table/column layout and tagged transactionally;
the schema version stays 2 and payloads are not rewritten. Other stores are refused
without migration. Plan ownership/version checks run inside the migration transaction.

The loopback UI keeps unsaved calculator inputs and journal previews when SQLite fails.
It reports that a write could not be confirmed, rather than claiming success or
automatically retrying. Users must reload the saved revision before retrying. Malformed
tokens/UTF-8/framing are rejected; stalled reads have an inactivity timeout. This remains
a single-owner local application, without a public-server security claim.

Keep sources and user exports private as appropriate. No credentials, provider transport,
telemetry, desktop shell, secure-erasure mechanism or license grant is added. The operating
guide describes retention, schema compatibility, backups and the exact ledger filename.

Text uses canonical LF through .gitattributes so manifest checksums are portable. This
does not change the brief, roadmap or earlier immutable continuations in Git content.

Gates A/B remain UNVERIFIED; Phase 03 real integration and p1-catalog remain BLOCKED,
Phase 04 real acceptance incomplete, Phase 05 DEFERRED. Visual/keyboard QA stays deferred.
Release readiness, real pilot and performance targets need their own evidence. A draft
Phase 06 checkpoint is not a merge, deployment or release.
