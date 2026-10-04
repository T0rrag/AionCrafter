# ADR 0005 — Continue engineering without browser QA as a development gate

Date: 2026-10-04. Status: user-directed sequencing update.

The user instructed: "ignore the cloud current -in progress chromium- stuff.
Continue with normal development. Create a new chat for each phase".

Treat this as direction to stop spending development iterations on cloud/Chromium
troubleshooting and to continue feature engineering from the tested calculator.
The next eligible phase is Phase 04 (crafting intelligence), beginning with p4-batches.
Phase 03 automatic prices and Phase 05 overlay remain deferred under ADR 0003.

The tested Phase 02 engineering is a sufficient dependency for synthetic Phase 04
work. Phase 02's outstanding visual, owner and pilot acceptance stays recorded for
later review; it is no longer the next development action. This exception does not
claim those checks passed, mark incomplete tasks COMPLETE, approve a release, or
supply real catalog/source rights. Keep the 42 stable IDs and Gates A/B unchanged.

Use one new chat inside the same Aion2 project for each new development phase.
Prepare and verify the checkpoint, create/verify the next chat where supported, then
stop writes from the previous chat. A prepared branch or starter alone is not a
created chat. If no authenticated chat-creation route is available, state the exact
limitation and provide the ready starter; do not substitute an unrelated Page,
local transcript, or sub-agent for a user-visible project chat.

Phase 04 may be explicitly stacked on unmerged Phase 02 PR #3; record the actual
base SHA and dependency in its future draft PR. Preserve no-merge/no-force-push.
Start with pure deterministic recursive batch expansion and meaningful tests, then
integrate into the existing manual workflows. Do not add guessed prices, fee rules,
probabilities, live providers or overlay dependencies. Revisit browser tooling only
when requested or when a working environment is supplied; do not let it dominate
normal feature development.
