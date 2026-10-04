# Phase 04 to Phase 06 — manual groundwork handoff

2026-10-04. Brief v1.3 / ADR 0007 / ADR 0008. Phase 04 remains IN_PROGRESS for real
catalog/rule/market integration; the independent manual groundwork has been merged.

## Verified baseline

PR #6 https://github.com/T0rrag/AionCrafter/pull/6 is merged under the user's standing
authorization. Tested head: e34ddf478c63777a0e0555664337d7eed2900134.
Merge commit: a185d0618cb315aa9468aec0de7716ccb1d56146.
HTTPS fetch and complete tree comparison matched the tested candidate exactly. Receipt:
docs/delivery/phase-04-merge.json. A documentation-only receipt follows on main; fetch it.
No force-push, concurrent overwrite, unrelated PR merge or permission change occurred.

`python -m unittest discover -q`: 238 passed on Windows/Python 3.12.14 (21.480s).
Compileall, synthetic catalog CLI validation and diff checks passed. Pre-merge bootstrap:
42 IDs, 109 checksums. Remote reviews/comments/statuses/PR workflow queries returned
empty lists, not a remote CI pass. Validation is synthetic/local, not game or visual QA.

## Delivered and deliberately limited

Recursive batches merge shared demand, carry leftovers and consume owned stock once.
Exact buy/craft costs include all executed fees. The bounded strategy family excludes
mixed buying/crafting of one variant and simultaneous competing producers; no general
optimum claim. One-attempt scenarios preserve alternative versus joint/bonus outcomes,
exact expectations, failure costs, unknown evidence and downside. Independent bonus
contracts require an explicit independence attestation; no guessed probability defaults.

Conditional rankings filter profession/requirements/vendor/stock/budget/tradability and
price completeness/source age, with visible exclusions. Price stock is never completed
sales volume; volume samples are explicit, scoped intervals and never summed by guess.
Local `/ledger` records opening stock, purchases, actual crafts/failures, sales/fees,
FIFO historical basis and original-estimate comparisons. Unknown basis stays unknown;
unsold stock is not realized revenue. Preview/save/load/export/import use a separate
append-only SQLite store with expected-revision checks. No source credentials or APIs.

p4-batches and p4-ledger are COMPLETE for independent engineering. Other Phase 04 tasks
remain IN_PROGRESS for real evidence/integration/acceptance. Preserve those statuses.
Phase 03 real adapter/reconciliation/activation and p1-catalog remain BLOCKED. Phase 05
is DEFERRED. Gates A/B UNVERIFIED. All fixtures and regression attestations are SYNTHETIC.

## Next eligible work and writer boundary

Start Phase 06 — Manual-edition validation and guidance, Part 01 in a separate chat in
the existing Aion2 project. This Phase 04 writer stops application edits. A handoff is
not evidence of a new chat or background work; none was started by this checkpoint.

Read AGENTS, PROJECT_STATE, backlog, current ADRs, both Phase 04 contract docs and brief
sections 14/20/21. Recheck heads. phase/06-release was absent from remote refs at receipt
time; create it from current reviewed main if still absent, otherwise verify ancestry
and preserve its history. One writer and one phase PR; publish/verify coherent increments.

First independent Phase 06 work: math acceptance coverage, migration/rollback and outage
evidence, input/privacy/storage review, installation/update/backup/retention guidance.
Do not claim the manual edition released without its applicable quality criteria.
Real pilot (100 items/25 recipes and 20 workflows) remains evidence-dependent. The owner
deferred visual/keyboard QA and real-game testing until after feature development;
do not restart Chromium troubleshooting or silently mark those checks passed.
