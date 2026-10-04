# AionCrafter working instructions

Read `docs/PROJECT_STATE.md` and the latest handoff first. Then read only the relevant master-brief sections and task definitions. The authoritative brief is `AionCrafter_Project_Prompt.md` v1.3; workflow rules are in sections 20–21.

The repository contains the architecture baseline and the tested Phase 01 data foundation. Phase 00 and Phase 01 remain incomplete. Preserve the existing 42 IDs and evidence-backed statuses. Keep the architecture control chat for decisions/review and implement in phase-scoped development chats.

Follow the current PROJECT_STATE and ADR 0003 for sequencing: Phase 01 engineering passed 47 tests; `p1-catalog` remains blocked. The next eligible development chat is Phase 02, using explicit synthetic fixtures until the pilot market and a permitted real catalog are available. Phases 03 and 05 are DEFERRED. Preserve phase-scoped chats and record any stacked PR dependency. Gate A (authorized automatic prices) and Gate B (supported overlay) remain UNVERIFIED. Do not guess an external API, region, tax, proc probability or catalog licence.

Use exact monetary representations. Missing prices are not zero. Keep market/build/variant identity separate from localized display names. Preserve input source and observation times. Test pure contracts/imports before application integration.

Verify repository, default branch and head before modifying remote state. Use one phase branch and PR per phase; keep partial work marked IN_PROGRESS. The user authorized phase-related uploads, not automatic merges or visibility/permission changes. Never force-push or overwrite concurrent work.

At every checkpoint: record changes, actual test commands/results, task statuses and blockers; prepare the next starter; commit/push when available; read back and report the verified SHA. Stop at the current phase boundary. Never claim new chats, remote uploads, completed tests or passed gates without evidence.
