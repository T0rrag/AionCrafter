# Phase 02 to Phase 03 groundwork handoff

2026-10-04. Supersedes the previous next-Phase-04 starter under ADR 0006. The user
requested Phase 03 preparation and a continuation prompt. No Phase 03 implementation,
branch, PR or new chat is created by this handoff.

Fetched Phase 02 at 1bea9e9d687458eb78921fee31a979a568cbe3ae with a clean working tree.
Main is 81f6493999b6bca1e86cd621e7815f7d05944020 after PR #4 merged the earlier
48dc8a3 checkpoint; git diff confirms only docs differ from Phase 02. PR #3 remains
open/draft. Do not infer Phase 04 implementation from PR #4's branch name. Main has
the tested application but older sequencing docs; carry this handoff, current state,
ADR 0006 and starter into the new branch after rechecking its base.

Phase 02 provides both direct-ingredient workflows, exact economics, source-aware
manual/vendor/snapshot observations and age, inventory/cash/replacement cost handling,
and immutable saved plans with validated transfers. Baseline: 95 tests passed.
Owner accepted calculator behaviour and marked review done. Visual QA stays deferred;
real-game pilot is after phase feature work. No permitted real catalog/provider has
been verified. Source rights cannot be deferred past connection.

Begin p3-freshness using existing contracts, a synthetic provider and injected clock;
then independent p3-resilience and p3-depth. Real adapter, reconciliation and release
remain blocked on their external evidence. Do not guess access, quotas, prices, scope
or game fees. Phase 04 recursion/buy-craft remains separate. Preserve all 42 IDs.

Documentation-only checkpoint: no new application test run. Existing 95-test results
remain the baseline. Refresh manifest and run python3 scripts/validate_bootstrap.py
plus git diff --check before publication. docs/NEXT_CHAT_PROMPT.md is the full starter.
Keep one writer and separate phase chats in Aion2. No merge/force-push or chat-creation
claim. Save and verify actual tests, SHAs and next instructions at each checkpoint.
