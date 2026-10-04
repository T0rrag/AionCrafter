Continue AionCrafter Phase 03 — Market-price groundwork, Part 02, in Aion2.
Fetch https://github.com/T0rrag/AionCrafter and verify actual remote heads before writing.
Resume phase/03-market-prices / draft PR #5, based on main
81f6493999b6bca1e86cd621e7815f7d05944020; no dependency on old draft PR #3.
Read AGENTS.md, docs/PROJECT_STATE.md, handoffs/phase-03-part-01.md,
PHASE_03_GROUNDWORK.md, backlog.json, delivery/phase-03-part-01.json and ADR 0006.

Part 01 implemented synthetic freshness, resilience and quantity/depth contracts;
137 full-suite tests passed on Windows/Python 3.12.14, including 42 Phase 03 tests.
First inspect whether authorized provider/market evidence has become available. Without
it, retain p3-adapter/reconcile/releaseprice BLOCKED and review the groundwork offline.
No real connection or automatic-price activation without required permission/evidence.
Gate A/B remain UNVERIFIED; p1-catalog BLOCKED; Phase 05 DEFERRED.

All three groundwork task IDs remain IN_PROGRESS pending adapter/application integration.
Preserve all 42 IDs. Phase 02 behavior accepted; visual QA deferred; real-game pilot after
phase work. No Chromium troubleshooting. One active writer, same branch/PR, tested
increments with verified remote SHA/tree and updated handoff. No merge or force-push.
Stay within Phase 03; Phase 04 requires a separate chat and its own handoff.
