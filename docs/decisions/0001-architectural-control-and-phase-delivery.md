# ADR 0001 — Architectural control and phase-scoped delivery

Date: 4 October 2026
Status: User-directed workflow; implementation details recorded for the next session

## Context

The user requested that this conversation serve as `Aioncrafter - Architectural control`, with development in new chats in the same project and GitHub uploads by phase. They supplied a v1.2 master prompt and bilingual HTML roadmap.

## Decision

Keep architecture/review here and implementation in phase-specific chats. Preserve Phase 00–06 and all 42 task IDs. Use one GitHub repository and phase-specific branches/PRs, with verified commits and explicit handoffs. The intended repository is `T0rrag/AionCrafter`; new visibility defaults to private. Owner/architectural review precedes merging.

Phase 01 may begin with explicit synthetic fixtures while real-market/catalog prerequisites are open. This does not complete Phase 00 or Phase 01's real-catalog import task. Do not develop Phase 02 in the Phase 01 chat.

## Actual capability findings

Connected GitHub login verified; no matching repository in the accessible owner listing. No repository-creation action in the connected toolset. No GitHub CLI login or recorded signed-in browser profile. No chat-create/rename action was available. No remote changes or ChatGPT UI changes were performed.

## Consequences

Prepare the documentation baseline and Phase 01 starter locally. The user still needs to rename/open chats and create the target repository (or provide an appropriately authorized tool route). A future session must verify the latest state rather than trust these findings indefinitely. Implementation is deliberately not begun in the control chat.
