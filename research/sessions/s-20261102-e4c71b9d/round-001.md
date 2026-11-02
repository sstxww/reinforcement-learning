# Round 001 — masked-mean card pooling (completed; no observed gain)

- Session ID: s-20261102-e4c71b9d
- Base main commit: 6ac59235b8238196a0e6462de77b72413c829372
- Independent branch: agent/s-20261102-e4c71b9d/optimization-001
- Source/head at execution: 3e222cb4290fe0e1d05d220f1ed5b6bd95f32e68
- Evidence commit: a5bc1a01e81e7b9555c4bdbecf5abc050adddfd3
- Exact run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413669679
- Run result: success; 14 unit tests passed
- Game engine: TavernGym 1.1.0, fingerprint 6d8712c93022ba11
- Upstream: fb61201a557ddd36a411cf44aac51ce4d9b606ce
- Patch SHA256: 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0
- Observation/actions: 4017 floats, 447 card indices, 245 maskable actions, N_CARDS=3984

## Hypothesis and related work
An extra masked mean card-embedding branch alongside the position-sensitive
card path will lower average placement relative to the unmodified extractor.
Primary metric: candidate average rank minus control average rank (lower is
better), using identically seeded trained policies and held-out complete matches.

Main research/sessions and knowledge/proposals were empty at the start.
Open PR #6 baseline, #7 evaluation, #8 infrastructure, #9 learning were
all drafts. They provided collision warnings, not validated improvements.
This session changed only new card_pool.py, card_pool_experiment.py and its
unit test, own isolated workflow and own research/experiment files. Neither
shared train.yml nor an unowned module was edited.

## Real bounded training
Workflow: .github/workflows/experiment-s-20261102-e4c71b9d.yml
Command: python -m tavern_ai.card_pool_experiment --steps 128 --seed 32000 --games 2

- Algorithm: real MaskablePPO, MultiInputPolicy, single-seat TavernEnv
- Seed: 32000 for each fresh model
- Total actual training: 256 steps (128 original control; 128 pooled)
- Both: n_steps=128, batch_size=64, n_epochs=2, gamma=.99,
  gae_lambda=.95, lr=0.0003, ent_coef=.01, cpu with two threads
- Actual control training time: 1.71 seconds (model creation/learn/save overhead
  makes direct speed comparison unsuitable); model SHA256:
  439e3a830978cb0a911e0985109fad2b5619a08e69bcbd436ca2ad83c8314ffa
- Actual pooled training time: 0.25 seconds; model SHA256:
  1ab6a4beefe060a38f5152dcdbb0e0473a26be87d058f0a41b571a645282ec2c
- 90-minute wall-clock limit, no ranked TavernArena games

## Real, independent eight-seat games
All completed by actual Game/bot_play until Game.is_over()==True; original
engine patched and verified. All had 0 illegal actions, 0 truncated combats,
and false turn_limit_end. Seat 0 controlled by the named policy. Other seven
seats used simulator bot_play(). All receipts preserved as JSON.

| Policy | Seed | Seat 0 rank | All 8 seats' ranks | Decisions | End-turn budget fallbacks |
| --- | ---: | ---: | --- | ---: | ---: |
| Official baseline | 32010 | 8 | [8,3,4,5,6,2,7,1] | 46 | N/A |
| Original PPO extractor | 32011 | 8 | [8,6,1,3,4,7,5,2] | 348 | 5 |
| Original PPO extractor | 32012 | 8 | [8,3,7,2,1,6,4,5] | 233 | 3 |
| Pooled PPO extractor | 32011 | 8 | [8,4,1,6,7,3,5,2] | 357 | 5 |
| Pooled PPO extractor | 32012 | 8 | [8,2,1,7,4,5,3,6] | 409 | 6 |

Seat-0 policies used a 65-actions-per-turn end-turn budget if legal to avoid
cycles; fallbacks are explicitly counted. This is a safety layer, not a proven
strategy improvement.

Baseline receipt: experiments/s-20261102-e4c71b9d/001-32010.json
Pooled receipts: experiments/s-20261102-e4c71b9d/001-32011.json,
experiments/s-20261102-e4c71b9d/001-32012.json
Original control receipts: reports/s-20261102-e4c71b9d/control-32011.json,
reports/s-20261102-e4c71b9d/control-32012.json
Complete quantitative A/B data: reports/s-20261102-e4c71b9d/ablation-001.json

## Before/after comparison and conclusion
- Original control 2/2 completed, mean rank 8.0, top-four 0/2, wins 0/2.
- Pooled model 2/2 completed, mean rank 8.0, top-four 0/2, wins 0/2.
- Mean rank delta candidate-control: 0.0; **no observed benefit**.
- Forced end turns: original control 8, pooled model 11 total.
- The exploratory two-game paired sample and tiny PPO budget do not establish
  equality or inferiority/superiority statistically. The extra embedding path
  has no demonstrated payoff under the tested setting.

## Failure analysis, reusable lessons and next hypothesis
128 learning steps are too small for a high-dimensional 4017+447 observation and
245-action game to infer meaningful strength. The observed failure is
consistent with learning/exploration constraints, not proof that pooling is bad.
A new pooled branch should not be promoted over the established extractor.
Action choice also remained susceptible to action loops requiring end-turn
fallbacks. A targeted next experiment should first test action-repeat-aware
masking or end-turn constraints on a dedicated experimental wrapper, with
longer controlled training budget (>=2048 steps) and >=10 held-out seeds,
without editing active strategy/learning PR files.

## Checkpoint and cleanup provenance
Model files were kept out of Git and uploaded only to Action artifact:
https://github.com/sstxww/reinforcement-learning/actions/runs/41413669679/artifacts/13127355102
Artifact: card-pool-s-20261102-e4c71b9d, 16,289,022 bytes,
expires 2026-12-02T08:34:39Z (NOT permanent).
In artifact: checkpoints/s-20261102-e4c71b9d/control.zip and pooled.zip
with corresponding .metadata.json files; SHA256s above.
Download artifact, verify zip hashes, install matching pinned engine/deps,
then use sb3_contrib.MaskablePPO.load(path,device="cpu") for inference.
Without durable backup, the model is NOT permanently persisted.
No temporary rollouts, caches, or oversized training logs committed.
