# Round 002 — official-bot behavior cloning: genuine negative replication (REJECT)

## A. Session / provenance
SESSION_ID `s-20261102-661adf61`, branch `agent/s-20261102-661adf61/optimization-002`, derived only from own R001 commit `3f452370f502627ad75c2c83b4da6cfcfbf60da7`, original main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`. R001 [PR #62](https://github.com/sstxww/reinforcement-learning/pull/62) passed independent CI [#41420672288](https://github.com/sstxww/reinforcement-learning/actions/runs/41420672288). R002 [real official-bot experiment #41421174913](https://github.com/sstxww/reinforcement-learning/actions/runs/41421174913) **success**, all test, engine, checkpoint restore and game evaluation stages completed. R002 PR/CI must be independently checked before integration.

## B. Game-rule source and substantive hypothesis
Pinned `TavernGym 1.1.0`, upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, engine source `6d8712c93022ba11`, actual public observe2 4017 numeric / 447 card slots / 245 masked actions, vocabulary 3984. Official `Game.bot_action(0)` is the teacher, with real seat-0 public observations and legal masks as training inputs; no future shop/RNG/hidden opponent information is passed to the learner. Rule action classes verified with offline regression tests and actual engine. See `mechanisms-001.md`.

Hypothesis: stronger official game-bot labels should improve BC compared to an extremely weak V0 baseline teacher. Previous R001: 128 V0 teacher transitions and 80 BC updates, raw rank 7 on one seed; R002 compares against it without assuming an improvement.

## C. Actual supervised training
- Three real official teacher training games on seeds 65101, 65102, 65103: complete, teacher ranks **[1,5,6]**, **485** teacher-labeled public observations.
- 80 supervised Adam minibatch updates at LR=0.001, batch 64, random seed 65100; architecture the same as R001 MaskedBC. PPO timesteps **0** (not reinforcement learning). First minibatch cross-entropy 3.5101573467; last 0.8967679143. These values are not tournament performance.
- Official training teacher action histogram: End 37, Refresh 33, Upgrade 15, Hero power 10, Buy **61**, Sell 42, Activate 22, Choose 96, Play 169, Freeze/Magnetize/Move 0. Histogram describes this sample, not a complete mechanism inventory.
- Independent official teacher imitation accuracy on 10 unseen teacher-game trajectories approximately 566/1169=48.4% total. Much lower than weak V0 teacher imitation accuracy in R001; direct comparison is confounded by different teacher and state distributions.
- Old checkpoint `b77aab475a502dacd2c036f4df87cbadd4656299bf5baaa13f16569b04699cd8` was **actually downloaded from R001 Actions artifact and hash verified** before this run. New official BC model SHA256 `0e53f1dba1d65e1d8066a5d48f4988c68968b226ba33521eb5666922abcca509`.
- New checkpoint artifact **#13130016943**, name `official-bc-s-20261102-661adf61`, expiration **2026-12-02 09:32:14 UTC**. Not permanent. Do not overwrite Champion.

## D. Real eight-seat independent evaluation
Exactly 10 new held-out seeds 66901–66910, paired by seed, four independent seat-0 policies each against seven official TavernGym bots. All **40/40** held-out games and all **3/3** new training-teacher games completed with genuine engine termination, no simulator guard/truncated combat. All four trained policy test variants are **raw (unprotected)**, 0 forced end turns. Each complete game record is inside `reports/s-20261102-661adf61/002-official-bc.json`, with seven independently preserved sample receipts under `experiments/s-20261102-661adf61/002-*.json`.

| Policy | n completed | Ranks on seeds 66901..66910 | Mean rank | Top 4 | First |
| --- | ---: | --- | ---: | ---: | ---: |
| Official scripted bot | 10/10 | 6,7,4,7,7,2,5,2,7,4 | **5.10** | 40% | 0% |
| V0 baseline teacher | 10/10 | 8,8,8,7,6,8,8,6,8,8 | 7.50 | 0% | 0% |
| Old R001 raw BC | 10/10 | 8,8,8,7,7,8,8,7,6,8 | 7.50 | 0% | 0% |
| New official raw BC | 10/10 | 8,7,8,8,8,8,8,8,8,7 | **7.80** | 0% | 0% |

Paired mean rank new BC minus old BC **+0.30** (worse), new BC minus V0 **+0.30**, new BC minus the teacher **+2.70** (worse). Same evaluation seeds are held out from both train sets. Small n=10; the old/new difference is not enough to claim a statistically generalizable degradation. Nevertheless there is no evidence to promote new BC, and the bot-to-student performance gap is large on these seeds.

## E. Root cause hypothesis / limitations
No technical test failure occurred. The failure is **capability transfer**: a better real teacher produces many diverse play/buy/sell/choice actions and higher ranks, but student trained on 485 state/action samples with 80 updates reproduces only ~48.4% of held-out teacher decisions and remains rank 7–8. The teacher and V0 trajectories visit different states and have unequal sample counts, so one cannot uniquely attribute this outcome to teacher quality. R001 learning could overfit simpler action labels. Rules correctness and teacher imitation do not imply strategy quality.

## F. Promotion / integration / next
**REJECT** promotion of new model. Retain honest reproducibility evidence and action-distribution diagnostic; integrating code as research-only is optional, not a Champion update. A useful next test is stratified action diagnostics (buy availability vs actions, economic phase, choose option, board development) and larger high-quality multi-seed teacher collection with validation holdout, perhaps with explicit stage auxiliary tasks or stronger structured state architecture. Do not repeat 80 updates on the same small sample without addressing capacity/coverage. This session has consumed its two planned bounded real-engine experiments; no background tasks or further training claimed.

## G. Reproduction
`python -m pytest tests/test_bc_session_661adf61.py tests/test_bc_official_session_661adf61.py`; `bash scripts/bootstrap_engine.sh`; download R001 artifact from run 41419937945 and SHA-verify `bc-model.pt`; `python -m tavern_ai.bc_official_session_661adf61 --old-model <path> --outdir experiments/s-20261102-661adf61/r002`. Never use unpinned or hidden engine data in inference.
