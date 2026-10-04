# Phase-based GitHub delivery

## Current status

Target: `T0rrag/AionCrafter` (intended, not created or published by this bootstrap). Authenticated account `T0rrag` was verified through the connector. No remote commit, branch, issue, PR or release has been created.

## One-time setup

Create a private repository named `AionCrafter` in `T0rrag`, initialized with a README. A GitHub CLI alternative, executed by the user in a signed-in environment, is:

```bash
gh repo create T0rrag/AionCrafter --private --add-readme
```

This command has NOT been run. Verify GitHub CLI authentication normally; never paste a token into chat. Ensure the ChatGPT GitHub connection can access the new private repository. Do not broaden access to unrelated repositories unnecessarily.

Official CLI reference (checked 4 October 2026): https://cli.github.com/manual/gh_repo_create

## Publication sequence

Read the existing repository/default branch and the relevant file contents before writing. Do not overwrite an existing project because its name matches. First publish this document package to `phase/00-architecture-bootstrap`, based on the verified default branch, and open a review PR. This is documentation setup, not completion of Phase 00's market/platform checks.

After architectural review, merge that baseline only with authorization. Phase 01 uses `phase/01-data-foundation`. When the baseline remains unmerged, either wait for review or explicitly stack Phase 01 on the documentation branch and set the PR base accordingly; never conceal that dependency. Rebase/retarget without force only under an agreed safe workflow.

Later branches: `phase/02-manual-calculator`, `phase/03-market-prices`, `phase/04-crafting-intelligence`, `phase/05-overlay`, `phase/06-release`. Create them when needed, not as proof of progress.

Use one coherent implementation per phase branch. Commit and push tested checkpoints; several chats can contribute to one phase PR. No automatic merge, force-push, unrelated upload, visibility change or branch-protection modification is authorized by this convention.

## Commit and PR format

Example commit title: `feat(phase-01): define item and market identity contracts`.

Include stable task IDs, relevant decisions, and test evidence in the commit body or PR. Use the supplied PR template. A partial phase stays draft/IN_PROGRESS. Ready for review does not imply that external gates have passed or that the app has been released.

## Verification receipt

After every upload, read back the remote branch/commit and report:

```text
Repository:
Branch and base:
Verified commit SHA:
Task IDs / phase status:
Tests actually run:
PR URL and draft/review state:
Gate A / Gate B:
Remaining work / next chat:
```

Do not insert invented URLs or SHAs. Local archive checksums and local commits are not remote-upload receipts. No perpetual/background delivery job is configured; publish only work actually performed in the active development session.
