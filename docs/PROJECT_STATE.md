# AionCrafter — Phase 06 manual-edition validation

2026-10-05 · Brief v1.3 / ADR 0007–0010. Phase 06 IN_PROGRESS, Part 03 delivered.
Gates A/B UNVERIFIED. All seven phases and 42 stable task IDs preserved.

## Repository and verified checkpoint

Repository: https://github.com/T0rrag/AionCrafter
Active branch: phase/06-release; target main. Draft PR #8 remains open/unmerged.
Verified base main at Part 03 start: e90c295b38245e57cf53a017d96885a770ed399f.
Verified Part 02 documentation head: cff1913271330ccb37fa47f71fb0cb279df44a71.

Part 03 tested implementation checkpoint:
0ad954dc2fcb5a564544fe397f81f09c7a7dc89c, tree
7ba2809b443efacb093069f16c98eb67e8c00868. GitHub Actions run 37328773165
checked out that exact SHA and completed successfully on CPython 3.12.14. Documentation
follows the tested implementation; the next writer must fetch actual heads before writing.

## Delivered and tested

- p6-mathqa remains COMPLETE from Part 01.
- Part 02 recovery/export evidence remains intact; p6-patches stays IN_PROGRESS because
  real-provider health/version integration is unavailable.
- Part 03 adds a deterministic validation-only source-checkout ZIP builder. It uses a
  fixed archive root/timestamp/mode, stable ordering and stored entries, excludes runtime
  caches, refuses overwrite and embeds metadata that explicitly says license status is
  unresolved and public_release=false. It does not create a wheel or public distribution.
- Two independent builds on the exact implementation SHA were byte-identical with SHA-256
  c03bac34b62271f5fbed3b16c488445cfc2712ba835de79b414ff52ac1718132.
  CI extracted that archive into a clean directory, created a clean venv and validated
  the SYNTHETIC catalog plus repository bootstrap from the extracted source tree.
- The deterministic cached-calculation benchmark primes one SYNTHETIC provider fetch,
  then measures PriceCache cached hits plus synthetic-bar item_economics. Run 37328773165
  used 250 warmups and 2,000 measured samples on Linux x86_64 / CPython 3.12.14,
  AMD EPYC 7763, 4 logical CPUs. p50=0.386905 ms, p95=0.449492 ms,
  p99=0.521868 ms, max=0.885099 ms; the proposed <300 ms p95 threshold was met for
  this SYNTHETIC workload only.
- The same run passed 271 tests in 16.036s, compileall, synthetic catalog validation and
  bootstrap with 42 stable IDs, 131 artifact checksums, 9 completed tasks with evidence
  and Gates A/B unchanged.

The brief's release performance criterion names pilot datasets. This synthetic benchmark
does not satisfy that real-pilot requirement and is not provider/browser/overlay latency.

## Remaining phase work and exact next task

p6-patches/security/package remain IN_PROGRESS. p6-package now has reproducible Linux
source-artifact and isolated-install evidence, but the redistribution-license decision
and cross-environment source-install acceptance remain open. The next independent Part 04
task is to validate the same source-checkout installation/update-removal path across
declared Linux and Windows CI environments without publishing a package or inventing a
license. Keep any environment-specific result explicit.

p6-usertest is BLOCKED on permitted real data, a declared real market and 20 real
workflows. p6-golive is BLOCKED on applicable pilot/quality evidence. Visual/keyboard QA
remains deferred by the owner. Do not restart Chromium/cloud-browser troubleshooting.

## Preserved earlier work and external blockers

Phase 04 manual groundwork is merged; p4-batches/p4-ledger COMPLETE for independent
engineering, while p4-buycraft/proc/liquidity/rank remain IN_PROGRESS for real catalog/
rule/market integration and acceptance. Phase 03 remains IN_PROGRESS with real adapter/
reconciliation/activation BLOCKED. p1-catalog BLOCKED. Phase 05 DEFERRED.
Gates A/B UNVERIFIED. No provider permission, quota, fee or probability is invented.

No public release, deployment, real-game pilot, visual QA, automatic-provider activation
or production-security approval is claimed. GitHub is the durable continuity source; the
next writer remains in Phase 06.
