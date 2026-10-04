# ADR 0007 — Authorized merges and autonomous phase continuation

2026-10-04. The user stated: "you are allowed to merge, Continue autonously".
This supersedes earlier no-merge wording for reviewed/tested AionCrafter phase work.
It does not authorize force-push, overwriting concurrent work, bypassing GitHub required
checks, changing repository permissions/visibility, real-source connection without
permission/evidence, or passing an external gate without evidence. No bulk merge of
historical PRs is implied. Preserve one active branch writer and phase-scoped Aion2 chats.

PR #5's synthetic Phase 03 groundwork was rechecked: 149 local tests passed; the PR was
mergeable with no reviews or comments. GitHub returned no PR Actions runs or commit
statuses; this is not a remote CI pass. The draft was marked ready and merged with an
expected-head check at 4e10fad95444241e68e353d41c9d24b4958b1dd6.
Merge commit bd23f4166ffe276179843761dea8e95275efbce1 was read back, fetched, and its
complete tree matched the tested PR head. Main was unchanged at 81f6493 before the merge.

Merging groundwork does not complete Phase 03. p3-freshness/resilience/depth remain
IN_PROGRESS pending production/application and market acceptance; p3-adapter/reconcile/
releaseprice remain BLOCKED on evidence. Gate A/B UNVERIFIED; Phase 05 DEFERRED;
p1-catalog BLOCKED. The current checkpoint ends Phase 03 application writes.

Next eligible independent engineering is Phase 04, starting p4-batches in a separate
Aion2 chat, under master brief section 20.4 (continue an eligible phase when external
integration is blocked). ADR 0006's request to perform Phase 03 groundwork first has now
been fulfilled; this decision does not activate real market intelligence. Use synthetic
catalogs and manual references, exact deterministic recursion/yield/leftover semantics,
then p4-buycraft and other independent Phase 04 requirements with unknowns explicit.

Existing phase/04-crafting-intelligence at 1bea9e9d687458eb78921fee31a979a568cbe3ae contains
only an older documentation checkpoint, not Phase 04 features. Preserve it. Bring current
main into that branch with a normal merge, resolving historical docs to the current
handoff while retaining history; never force-reset/push. Recheck heads first. Open a new
Phase 04 PR against main because historical PR #4 is already closed/merged.

Save/verify the handoff before starting its chat. The next writer owns Phase 04; this
Phase 03 chat stops repository writes after dispatch. No new-chat claim without an actual
successful tool response and observed startup. Prior visual QA stays deferred; real-game
pilot follows phase feature development. No Chromium troubleshooting.
