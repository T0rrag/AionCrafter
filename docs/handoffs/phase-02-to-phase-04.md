# AionCrafter — Phase 02 engineering handoff to Phase 04

2026-10-04. Brief v1.3, ADRs 0003–0005. User now directs normal development and a new
chat for each phase; cloud/Chromium troubleshooting is removed from the active queue.
Phase 02 engineering is ready to support Phase 04 synthetic work, with outstanding
acceptance tracked separately. Phase 02 tasks are not falsely marked complete.

## Verified code and dependency

T0rrag/AionCrafter, phase/02-manual-calculator, draft PR #3 stacked on unmerged PR #2.
Fetched starting head 91a2479c94a26757fc34ca09bac1e9218ff82935; implementation
d355f7107d0a2205a61afc672f7c27f9b2146864. The starter/decision commit follows this head.
Phase 04 branch: phase/04-crafting-intelligence, to be based on the verified Phase 02
handoff commit. If it already exists, fetch and inspect it rather than replacing it.
Record actual base and stack dependency before the future Phase 04 draft PR.

Phase 02 provides exact deterministic direct-ingredient economics, inventory/cash vs
replacement valuation, scoped manual/vendor/snapshot observations with preserved age,
immutable saved-plan revisions, optimistic writes and lossless JSON/CSV transfers.
Reference IDs cannot change displayed records on replay. Plan DB v2 prevents stale
tabs overwriting a recreated name; JSON transfer schema remains v1.

## First Phase 04 increment

p4-batches: build a pure deterministic recursive expansion contract. Select recipes
explicitly when alternatives exist. Aggregate shared input demand before batch rounding,
track produced/required/leftover quantities, detect cycles, preserve catalog/build/variant
identities and expose unsupported stochastic or joint-output cases instead of guessing.
Start with the clearly bounded single-output deterministic path and synthetic tests for
shared intermediates, non-unit yields, exact batch boundaries, leftovers, cycle/unknown
outcome refusal and deterministic ordering. Read catalog.py/models.py/economics.py and
relevant tests before choosing the interface. Broaden outcomes only with explicit rules.
Later p4-buycraft compares declared objectives and feasible costs; never promise global
optimality from a simple per-node heuristic. Keep actual profit unknown without records.

## Validation and remaining evidence

The actual fetched baseline was rerun in this session: 95 tests passed on Python 3.12.14.
This handoff changes documentation/sequencing, not application code. Bootstrap checks
verify all 42 IDs and manifest consistency. Do not claim a new application feature here.
Visual/pilot acceptance is outstanding and deferred from the active engineering path by
ADR 0005. Synthetic catalog only (7 variants/3 recipes); p1-catalog BLOCKED; Phase 01
incomplete; Phases 03/05 DEFERRED; Gates A/B UNVERIFIED. No merge/force-push or release.

## Chat ownership

The next phase must start in its own Aion2 chat. This chat stops application writes at
this handoff. Save/verify actual chat creation and startup before claiming it exists.
No automatic conversion/synchronization of old local Codex transcripts is implied.

Chat-creation route inspected: no dedicated project-chat tool is exposed. The connected
browser reaches ChatGPT but is signed out; secure sign-in is required to access Aion2.
No next-phase chat has been created at this checkpoint. Do not use anonymous chat.
