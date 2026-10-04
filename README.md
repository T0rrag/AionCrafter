# AionCrafter

External AION 2 crafting-economics companion, inspired by Auctionator.

**Status:** architecture bootstrap only. No application implementation, live market feed or tested overlay. This package was prepared locally on 4 October 2026; it has not been uploaded to GitHub.

## Start here

Read `docs/PROJECT_STATE.md`, then `docs/NEXT_CHAT_PROMPT.md`. The full brief is `AionCrafter_Project_Prompt.md` v1.3. Open `AionCrafter_Roadmap.html` in a browser for the bilingual interactive roadmap.

Two planned workflows: item → materials → price references → estimated profit/loss; and a materials-only pricing list. The manual/reference edition does not require a live AH API. Automatic prices and an Overwolf overlay have independent unverified gates.

## Working model

The architecture conversation is designated `Aioncrafter - Architectural control`. Implementation belongs in separate phase-scoped chats in the same existing project. The next development session is `AionCrafter | Phase 01 | Data foundation | Part 01`.

Use one repository (`T0rrag/AionCrafter`, intended but not created by this package), phase branches, tested commits and reviewed PRs. See `docs/GITHUB_DELIVERY.md`. Do not merge or claim a release merely because a phase has been uploaded.

## Validate this bootstrap

```bash
python3 scripts/validate_bootstrap.py
```

This checks artifact integrity, backlog IDs and the HTML checklist. It is not an application test suite.

## Files

`AGENTS.md` contains focused working instructions. `docs/backlog.json` preserves all 42 tasks. `docs/decisions/` records architecture decisions. `docs/handoffs/` preserves session records. The empty application has deliberately not been scaffolded in the architectural-control chat.

No code/data distribution licence has been selected. No game assets or third-party price data are included. Not affiliated with NC, AION, Overwolf or Auctionator.
