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

New PPO training steps: **0**. No new model weights, Release, restore or paired model games claimed. Actual own read-only [GitHub Actions run 41512216069](https://github.com/sstxww/reinforcement-learning/actions/runs/41512216069) COMPLETED SUCCESS at SHA `824a47a090fbab1bb3315a62441c3adaaba3a29e`: local two-clone CAS regression, pinned engine bootstrap+contract and one complete baseline-controlled eight-seat game. Original ZIP Artifact ID `13173254450` downloaded and parsed; baseline seed 99841, seat 0 rank **8**, placements `[8,7,3,6,4,5,1,2]`, 14 turns, 35 actions, no truncation, receipt SHA256 `890a68e77e04e3a1669fccbb4b5e6a404f26345cf0f6267a31beb541bf436b3b`. Exact receipt under `experiments/s-20261103-f6497e7a/001-99841.json`; audit in `reports/s-20261103-f6497e7a/001-v7-claim-proof.json`. No PPO evidence, no new training, no weights. Prior published 1408-step V5 checkpoint is research context, not a newly verified checkpoint.

## Required next work

Actual live GitHub claim ref `claims/v7/eea1bc1baf2d37ef54955cbdffea8ca0` was created from metadata commit `3ef0dd71ed39d01151f91870c1551b484366dff7` and read back; lease expiry is explicit. Now open non-Draft PR, check exact-head PR CI and release task lease by CAS; require independent review and a separate real main integration lock before any merge. A separate truly serialized INTEGRATOR must decide merge after checking current main. Don't merge #15 before its #9 dependency. No Champion promotion.
