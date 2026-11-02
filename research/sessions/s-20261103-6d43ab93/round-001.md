# V7 Round 001 — test raw PPO seat invariance, not assumed improvement

## Inherit and triage

Full Gmail V7 TXT (32,014 bytes) read. Main at task claim `990acd21d598a34a554a80c50089a8f1a9423ac4`. Existing canonical evaluator `tavern_ai.canary.run` and `tavern_ai.evaluate` control only seat=0; prior rank-eight evidence is concentrated in that seat. Do not rewrite their contracts while other sessions are improving the shared trainer/evaluator. Existing PR #168 contains seed-matched raw PPO vs baseline at seat0; #174 audits durable Release drift; #172 covers guard source provenance; #179 audits stacked PR readiness. These are not equivalent to a seat1 controlled test.

## Falsifiable hypothesis

The recorded eighth-place symptom could be partially seat-specific. Run one matched, new seed 99741 with *controlled seat 1* and seven pinned-engine scripted opponents, first baseline then unassisted raw 1408-step model. If PPO fails action budget, classify incomplete and preserve raw-action trace; never invent rank 8 or fallback. If it completes, record actual placement and raw action histogram (no guessed engine-family mapping). Sample n=1 is exploratory and cannot prove seat effect or rank improvement.

## Implementation, safety and budget

Own script `scripts/v7_seat_probe_6d43ab93.py` and fixture-only unit suite `tests/test_v7_seat_probe_6d43ab93.py`. Pin TavernGym 1.1.0/source hash `6d8712c93022ba11`, observe2 4017/447, actions 245. Source checkpoint via canonical immutable Release `v5-s-20261102-68099929-1408-41428692617`, expected SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Restore must fail closed; never select a different source or silently initialize. At most 6000 controlled raw actions per arm, no assisted action, no forced ends. One own, read-only 70-min GitHub workflow; artifact retention 30 days, not durable model storage. No new PPO steps in this round.

## Execution and next gate

At creation time no new run/receipt exists. Do not equate workflow definition with execution. After push, read the real run and job, inspect authentic emitted receipt, ensure `Game.is_over()` and placements permutation, seat/rank identity, model hash match, and commit only original verified complete evidence. Preserve any failure as failure. Then create/update a non-Draft PR only when source and CI gates pass. This session does not have an exclusive main-merge lease, so must not merge even if PR passes its checks.

Proven historical 1408-step model seat0 heldout n=3 [8,8,8] vs paired baseline [6,8,8]; experimental outcome seat1 remains unknown.

## Actual results and post-run evidence (verified)

- Genuine model/baseline games completed [Actions run 41512471789](https://github.com/sstxww/reinforcement-learning/actions/runs/41512471789) SUCCESS, pinned source `2c434ad543b876a2335decd957a6b14b374a8199`.
- Both original Artifact JSONs downloaded; SHA256 verified, then independently fetched/checked in one-shot [archiver 41513283421](https://github.com/sstxww/reinforcement-learning/actions/runs/41513283421). Original archive was committed [a043c3d](https://github.com/sstxww/reinforcement-learning/commit/a043c3d85d6856a3bf33b0a1b6fc72503716a94d) and ephemeral write workflow retired.
- Seed **99741**, controlled **seat1**, seven scripted opponents each arm: baseline complete rank1 [7,1,5,4,8,6,3,2], decisions80, turns15; restored raw model complete rank8 [1,8,6,2,5,7,3,4], decisions123, turns16. Both zero fallback and forced end, truncation and turn limits. **No rescue policy**.
- Checkpoint immutable Release `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, downloaded/checksums/CPU loaded in source job; this session did not run optimizer or train new weights.
- Pinned action-family interpretation from existing main/merged #176: raw model action 2 FREEZE 70, action1 REROLL 41, BUY raw12 once. Baseline BUY actions total21. Mean placement descriptive baseline1/model8, paired delta+7 (higher worse), n=1; CI success is correctness evidence, **NOT** proof of policy gain or statistical significance. Public consecutive identical observation count 0 cannot rule out economically wasteful actions. No new Best or Champion.
- Original receipts `experiments/s-20261103-6d43ab93/001-99741-{baseline,model}.json`, report `reports/s-20261103-6d43ab93/001-seat1-raw-ppo-summary.json`. Artifacts temporary only. More complete held-out seat rotations, legal masked buy decisions and before/after public game state remain needed.
- Authenticated P0 review submitted on PR #174, but no exclusive integrator lease/merge; main at last check `c1b828734527bae6141805581693d890cc3bff94`, completed green CI [41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964), includes other agent merged #165. Our task branch is independent; one-shot temporary archiver removed after successful evidence commit.
- Next integration gates: create non-Draft PR, get **exact latest head** CI with genuine independent full-match and receipt check, recheck main base and security/reviews. Any merge only under unique validated main lock.
