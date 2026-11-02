# s-20261102-91b6e4a7 R001 — V5 P0/P1 checkpoint integrity integration

## Original state and parallel reconciliation
Original main SHA: `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`. Writable repository only `sstxww/reinforcement-learning`; upstream read-only; no Arena. Session branch `agent/s-20261102-91b6e4a7/optimization-001`, PR #93. Main gained #25, #26, #37, #39, #43, #47, #69, #70 and #87 during the audit; these were merged by **other integrator sessions**, not us. We did not remerge, modify or overwrite their branches.

PR #87 added canonical `models/registry.json` with four unpromoted historical Releases, V1 256/384 and V2 1280 steps. Our first separate registry was incompatible (add/add conflict); **repaired** by setting our branch `models/registry.json` to exactly main's blob and integrating its `tavern_ai.registry_integrity` API. Our unique code now adds *two-asset* Release integrity validation, including recorded metadata SHA256 checks, ZIP CRC, engine compatibility and step count. Main's `latest` is explicitly **latest experimental unpromoted** (not verified resumption). No Champion or Best.

## Actual finished branch experiment
[Own successful GitHub Actions #41427822784](https://github.com/sstxww/reinforcement-learning/actions/runs/41427822784) tested offline catalog and installed pinned TavernGym 1.1.0, source fingerprint `6d8712c93022ba11`, public 4017 floats / 447 cards / 245 masked actions. Original full eight-seat **baseline** game seed 91031 controlled seat 0, resulting place 8, 14 turns, 51 decisions, placements [8,1,5,2,6,3,4,7], true Game.is_over, 0 truncated combats / no turn-limit end. Authentic receipt is `experiments/s-20261102-91b6e4a7/001-91031.json`, committed at `65bf5ccc1a9f1dfaf7d9fef8aef7f95964cd4826`. This is an infrastructure test, not a neural policy performance test. Current updated code still requires latest-head PR CI.

PPO steps this session: **0**. New checkpoint: **none**. Release bytes redownloaded: **none**. Actual model-only full games: **0**. Candidate model improvement: **not claimed**. Existing V1/V2 releases and hashes are real GitHub API metadata but not freshly downloaded/reloaded by us. No model promoted.

## Reproduction
`python -m tavern_ai.checkpoint_catalog` checks the canonical integrated registry, including unpromoted latest identity. After independently downloading **both** matching Release assets, run:

`python -m tavern_ai.checkpoint_catalog --model-id v2-learning-41413557445 --weights /safe/path/model.zip --metadata /safe/path/model.metadata.json`

This checks both SHA256 values, ZIP CRC, engine contract and step count. It does **not** call MaskablePPO.load, recover optimizer state, perform a training step, or play a full model-controlled match.

## P2 rank-8 evidence and next falsifiable gate
Issue #78 and draft PR #60 observed 1e-4 low-LR candidate: 3 genuine model games [8,8,8], 36 actions, 0 BUY, 21 model-chosen END_TURN. The 3e-4 comparison: [8,8,7], 875 actions, 20 BUY, 21 guard-forced END_TURN and max repeated action streak 40. Raw 'other_action' group must be decoded using pinned actions; cannot call every one a no-op. Purchase affordability at the candidate's END_TURN states is still unknown, and LR causal attribution is unproven. The next step is a small trace of affordable legal BUY opportunities, before/after public state and no-progress loops, independent heldout games and then targeted behavior correction; stop bulk PPO until validated.

## Release/integration gates
Await exact latest-head PR CI, current-main compatibility and integrator review. This PR intentionally does not alter shared train.yml, PPO algorithm, baseline, central metadata registry or other session files. Main CI must pass after any authorized merge. No new model weight stored in Git and no official Arena game.
