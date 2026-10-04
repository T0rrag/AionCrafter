# ADR 0003 — Continue the manual edition; defer automatic prices and overlay

Date: 2026-10-04
Status: User-directed priority decision; implementation sequencing recorded below

## User direction

The user asked to continue development now and address live prices and overlay later.
Proceed with the manual/reference-price edition in a normal web application. Automatic
price access and the overlay are optional future integrations, not prerequisites for
building the calculator. This follows master-brief sections 11, 19 and 20.4.

## Current scope and dependency handling

- Phase 03 (permitted automatic prices) and Phase 05 (overlay) are DEFERRED.
  Their existing task IDs and requirements remain unchanged. Deferred is not complete.
- Gate A and Gate B remain UNVERIFIED. No integration is claimed to work or to be
  repairable without first obtaining its required access/support evidence.
- Phase 01 remains IN_PROGRESS, with p1-catalog BLOCKED on the real pilot and permitted
  verified data. This is a separate dependency from live-price access and overlay.
- Its tested engineering contracts are available for the next manual-calculator
  increment. Phase 02 development can use the explicitly SYNTHETIC catalog, as allowed
  by section 19, while the real-catalog task remains visibly unfinished. This does not
  declare the full Phase 01 dependency complete or authorize a real-data release.

## Next development phase

Next eligible development chat: Phase 02 — Manual-first calculator, Part 01.
First implement p2-economics using pure exact arithmetic and tests, then the manual
price editor and both user workflows: materials-only pricing and item economics.
Do not combine those requirements into a promise that every task fits one increment.
Use configurable, explicitly unverified fees and preserve missing-price/provenance
states. Retain provider interfaces so approved automatic data can be added later.

Honor the one-phase-per-chat workflow: prepare the starter here; implement Phase 02
in the next chat. Create phase/02-manual-calculator from the verified reviewed base,
or explicitly stack it on phase/01-data-foundation while PR #2 is unmerged. Record the
actual base SHA and PR dependency. This decision does not authorize merging either PR.

## Deferred integrations

Resume Phase 03 only after Gate A evidence (permission, working scoped samples,
timestamps/freshness and sustainable usage limits). Resume Phase 05 only after Gate B
evidence (exact client/framework support, approval and real-game interaction tests).
Neither deferred feature should block manual-edition engineering or be described as
already implemented. Provider outages and overlay packaging must remain separate
from the calculation core.
