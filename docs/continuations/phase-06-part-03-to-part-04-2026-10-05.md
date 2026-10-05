# AionCrafter continuation — Phase 06 Part 03 to Part 04

Date: 2026-10-05
Repository: https://github.com/T0rrag/AionCrafter
Active/next branch: phase/06-release; base main.
Active PR: https://github.com/T0rrag/AionCrafter/pull/8 — keep the same draft PR.
Canonical moving entry: docs/NEXT_CHAT_PROMPT.md.

## Verified checkpoint

- Part 03 started from branch head `cff1913271330ccb37fa47f71fb0cb279df44a71`.
- Main at Part 03 start: `e90c295b38245e57cf53a017d96885a770ed399f`.
- Tested implementation: `0ad954dc2fcb5a564544fe397f81f09c7a7dc89c`.
- Tested/fetched tree: `7ba2809b443efacb093069f16c98eb67e8c00868`.
- GitHub Actions run 37328773165 checked out that exact SHA and succeeded.
- Documentation follows the implementation. Fetch actual main/branch/PR heads and compare
  ancestry before the next write.

## Read first

AGENTS.md; docs/PROJECT_STATE.md; docs/NEXT_CHAT_PROMPT.md; this continuation;
docs/handoffs/phase-06-part-03.md; docs/delivery/phase-06-part-03.json;
docs/backlog.json; docs/TEST_RESULTS.md; docs/PHASE_06_VALIDATION.md;
docs/MANUAL_EDITION_GUIDE.md; ADR 0007–0010; AionCrafter_Project_Prompt.md sections
14, 20 and 21. Inspect the Phase 06 workflow and Part 03 scripts before changing scope.

## Delivered in Part 03

The deterministic source ZIP is validation-only, declares license unresolved and
public_release=false, and is not a wheel/signed installer/release asset. Run 37328773165
built it twice byte-identically and validated an extracted checkout in a clean venv.
Both builds on the exact implementation SHA had SHA-256
`c03bac34b62271f5fbed3b16c488445cfc2712ba835de79b414ff52ac1718132`.

The SYNTHETIC benchmark primes one provider call, then measures cached PriceCache +
deterministic synthetic-bar item_economics. Environment: CPython 3.12.14, Linux x86_64,
AMD EPYC 7763, 4 logical CPUs; 250 warmups / 2,000 samples; p50 0.386905 ms,
p95 0.449492 ms, p99 0.521868 ms, max 0.885099 ms. The proposed <300 ms target
was met for this SYNTHETIC workload, not for pilot datasets.

## Status boundaries

Phase 06 remains IN_PROGRESS. p6-mathqa COMPLETE; p6-patches/security/package IN_PROGRESS;
p6-usertest/golive BLOCKED. p1-catalog BLOCKED; Phase 03 real integration BLOCKED/
IN_PROGRESS; Phase 04 real integration incomplete; Phase 05 DEFERRED; Gates A/B UNVERIFIED.
The repository still declares no redistribution license. Do not publish the validation ZIP.

## Exact next implementation task

Continue Phase 06 Part 04 on the SAME branch/PR. Extend installation evidence across
explicitly declared Linux and Windows CI environments using the same source-checkout
validation artifact/path. Verify clean extraction/startup and a documented update/removal
procedure without publishing a package. Record environment-specific results separately.
Keep the license decision unresolved unless the owner explicitly supplies one.

Do not activate a real provider, begin Phase 05, restart Chromium/cloud-browser
troubleshooting, claim visual QA/pilot/release/deployment, or treat SYNTHETIC performance
as pilot acceptance. Preserve real-catalog/integration blockers and Gates A/B.

Before Part 04 ends, create a NEW immutable continuation and refresh NEXT_CHAT_PROMPT,
PROJECT_STATE, backlog/progress, TEST_RESULTS, handoff/delivery, manifest and applicable
guides. Run required tests/validators, publish only tested checkpoints, verify remote
SHAs/tree/CI/PR state, then stop the previous writer.
