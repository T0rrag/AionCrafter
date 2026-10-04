Continue AionCrafter Phase 03 — Market-price groundwork, Part 03, in Aion2.
Fetch https://github.com/T0rrag/AionCrafter and verify actual remote heads before writing.
Resume phase/03-market-prices / draft PR #5 against main. Read AGENTS.md,
docs/PROJECT_STATE.md, handoffs/phase-03-part-02.md, PHASE_03_GROUNDWORK.md,
backlog.json, delivery/phase-03-part-02.json and ADR 0006.

Part 01 implemented synthetic freshness/resilience/depth. Part 02 corrected mixed-batch
retry exhaustion and immutable IDs across manual/provider history. 149 full-suite tests
passed on Windows/Python 3.12.14, including 54 Phase 03 tests. Preserve those regressions.
First inspect whether authorized scoped provider evidence has become available. Without
it, retain p3-adapter/reconcile/releaseprice BLOCKED and Gate A UNVERIFIED. No real source
connection or automatic activation without required permission/evidence. Source rights,
production transport/shared quota ownership and application/market acceptance remain pending.

Preserve all 42 IDs and one active writer. Three groundwork tasks remain IN_PROGRESS;
Phase 01 incomplete/p1-catalog BLOCKED; Phase 05 DEFERRED; Gates A/B UNVERIFIED.
Phase 02 behavior accepted, visual QA deferred, game pilot after phase features. No
Chromium work. Publish tested increments and verified SHA/tree receipts on the same PR.
No merge/force-push; stay in Phase 03. Phase 04 requires a separate chat.
