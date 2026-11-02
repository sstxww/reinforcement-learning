# Round 001 — V7 cooperative atomic task reference

Session: `s-20261103-f6497e7a` | TASK_KEY: `coordination/v7-atomic-task-ref` | base main `3a745c6f6a48c65528bcbeb81b8627b8db93f046`.

## Inherited evidence / overlap

Read latest V7 Gmail TXT (32,014 bytes), AGENTS.md, docs/SESSION_PROTOCOL.md, docs/CLOSED_LOOP.md, main registry and manual training workflow. Observed PR backlog with stacked #15 -> #9; overlapping durable continuation PR #165. Main already contains verified restoration #117, SHA preflight #125, registry gates #154, latest #176; avoid duplicating shared training and evaluation paths.

## Hypothesis / implementation

A deterministic, task-key hashed Git branch ref with an *exact expected-old-SHA Git push lease* prevents cooperative sessions overwriting each other's task ownership and permits safe handoff using explicit release, unlike an issue comment or check-then-write. Owner and expiry are embedded in immutable audit commits. The helper does not grant merge rights: no protected Merge Queue, serialized integration workflow or verified integration CAS lease was established.

## Local reproduction

`python -m unittest discover -s tests -p 'test_v7_task_claim*.py' -v` passed 2 tests using 2 independent clones and a bare Git server. Tests show owner B blocked while A's claim valid; non-owner release blocked; stale expected SHA push blocked; A can renew/release; B can reacquire. Initial failed key-validation test led to stricter one-slash format and a green rerun.

## Command contract

`python scripts/v7_task_claim.py acquire --task-key coordination/v7-atomic-task-ref --session-id s-20261103-f6497e7a --ttl-minutes 30`

Then `inspect`, `renew`, `release` with same flags; requires a configured authenticated Git `origin`. Failure to push is *not* a lock. Do not conflate lease expiration with exclusive main merge authority, and never force-update main.

## Training / games / costs

New PPO training steps: **0**. No new model weights, Release, restore or paired model games claimed. Own baseline eight-seat CI probe queued separately after the workflow commit; results must be reviewed before updating this log. Prior published 1408-step V5 checkpoint is research context, not a newly verified checkpoint.

## Required next work

Inspect live Actions run and original receipt, commit exact eight-seat evidence; then check PR latest head CI and request independent review. A separate truly serialized INTEGRATOR must decide merge after checking current main. Don't merge #15 before its #9 dependency. No Champion promotion.
