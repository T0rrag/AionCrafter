# Draft: Phase 01 — versioned data contracts and transactional catalog storage

Target repository: T0rrag/AionCrafter.
Head: phase/01-data-foundation
Base: phase/00-architecture-bootstrap (stacked documentation dependency).
PR: https://github.com/T0rrag/AionCrafter/pull/2 — OPEN, DRAFT, UNMERGED.
Documentation dependency: https://github.com/T0rrag/AionCrafter/pull/1.
Keep draft pending real catalog and architectural review.

The data layer now identifies items by namespace/region/build/variant and prices by
explicit market/faction/currency, preventing cross-market joins. Strict imports reject
duplicate/ambiguous identities, orphan references, invalid values and crafting cycles.
Versioned SQLite snapshots retain the last known-good catalog when validation,
publication or concurrent-write checks fail, with explicit rollback and immutable
observation/calculation history.

Tasks: p1-identity, p1-recipe, p1-trade, p1-validate, p1-storage implemented and tested.
p1-catalog remains BLOCKED; fixtures contain seven synthetic variants and three
synthetic recipes. No production catalog, live provider, economics engine or UI.

Validation: `python3 -m unittest discover -v`, offline CLI import/inspect workflow,
and `python3 scripts/validate_bootstrap.py`; see docs/TEST_RESULTS.md for outcomes.
Gate A and Gate B remain UNVERIFIED. No merge authorization has been given.
