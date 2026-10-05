Continue AionCrafter — Phase 06 manual-edition validation, Part 04.
Repository: https://github.com/T0rrag/AionCrafter
Branch: phase/06-release; draft PR #8 against main.
Immutable continuation:
docs/continuations/phase-06-part-03-to-part-04-2026-10-05.md

FIRST fetch and verify actual remote main/branch/PR heads and ancestry. Part 03 started
from cff1913271330ccb37fa47f71fb0cb279df44a71; main was
e90c295b38245e57cf53a017d96885a770ed399f. Tested Part 03 implementation:
0ad954dc2fcb5a564544fe397f81f09c7a7dc89c, tree
7ba2809b443efacb093069f16c98eb67e8c00868. Documentation follows that SHA.

Read AGENTS, PROJECT_STATE, the immutable continuation, handoffs/phase-06-part-03.md,
delivery/phase-06-part-03.json, backlog, TEST_RESULTS, PHASE_06_VALIDATION,
MANUAL_EDITION_GUIDE, ADR 0007–0010 and brief sections 14/20/21.

Part 03 delivered a deterministic validation-only source-checkout ZIP plus isolated
clean-venv source startup and a declared SYNTHETIC cached-calculation benchmark.
GitHub Actions run 37328773165 on the exact implementation SHA passed 271 tests,
compile/catalog/bootstrap and both packaging/performance checks. Two archive builds were
byte-identical (SHA-256 c03bac34b62271f5fbed3b16c488445cfc2712ba835de79b414ff52ac1718132).
Benchmark: 250 warmups/2,000 samples, p95 0.449492 ms on CPython 3.12.14/Linux x86_64/
AMD EPYC 7763/4 logical CPUs. This meets <300 ms only for the SYNTHETIC workload.

Phase 06 remains IN_PROGRESS: p6-mathqa COMPLETE; p6-patches/security/package
IN_PROGRESS; p6-usertest/golive BLOCKED. Preserve p1-catalog and Phase 03 real-integration
blockers, Phase 04 remaining integration, Phase 05 DEFERRED and Gates A/B UNVERIFIED.
The redistribution-license decision remains unresolved; the source ZIP is not a release.

Exact next task: validate the same source-checkout installation/update-removal path across
explicit Linux and Windows CI environments. Keep it validation-only and record environment
specific evidence. Do not publish an installer/release asset or invent a license.

No Chromium troubleshooting, provider activation, Phase 05 work, visual QA/pilot/release
claim, force-push or check bypass. Use the same branch/PR and one writer. Before ending,
publish a NEW immutable continuation and refresh state/backlog/progress/tests/handoff/
delivery/guide/manifest/NEXT_CHAT_PROMPT as applicable; verify remote SHA/tree/CI/PR state.
