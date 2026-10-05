# ADR 0009 - GitHub continuation checkpoints

Date: 2026-10-05
Status: Accepted

## Context

AionCrafter development is intentionally split across phase-scoped ChatGPT/Aion2 chats.
Some Work conversations can be unavailable on another computer, so chat-history visibility
cannot be the only continuity mechanism. The repository already carries PROJECT_STATE,
handoffs, delivery receipts and NEXT_CHAT_PROMPT.

## Decision

GitHub is the canonical cross-device continuation source for development sessions.

Before a development chat stops writing, it must publish and verify an immutable continuation
under `docs/continuations/` and refresh `docs/NEXT_CHAT_PROMPT.md`. The continuation records
the verified tested/base/merge checkpoint, branch/PR, first-read files, completed work,
tests actually run, remaining backlog/gates/blockers, governing ADRs, explicit do-not-repeat
constraints and the exact next task.

The repository's normal PROJECT_STATE, backlog evidence, TEST_RESULTS, handoff/delivery and
manifest records are updated when applicable. The next chat always fetches actual remote
heads before writing; a continuation SHA is a verified checkpoint, not permission to assume
that no later documentation commit exists.

Immutable continuation files are never overwritten. NEXT_CHAT_PROMPT is the moving pointer
to the newest continuation.

## Consequences

Development can recover from another computer without access to a device-local chat.
Git history becomes the durable audit trail for context transitions. This adds a small
documentation/verification cost at the end of each chat but avoids losing phase state or
repeating completed work.

This ADR does not change any backlog status, provider authorization, Gate A/B state, visual
QA deferral, merge safety rule or release criterion.
