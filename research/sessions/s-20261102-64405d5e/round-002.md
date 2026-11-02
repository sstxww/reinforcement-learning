# s-20261102-64405d5e — Round 002: independent-seed confirmation of buy-before-play

## Hypothesis
Round 001's mean placement advantage of -0.1667 (six paired games) may generalize to disjoint random seeds. Keep the **identical candidate policy** and conduct a 20-pair independent evaluation, recording genuine Game.is_over receipts and an uncertainty interval. This round improves the evaluation methodology and sample size, not the shared production policy.

- R001 origin main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- This round branch: `agent/s-20261102-64405d5e/optimization-002`, branched from our own R001 report commit `0a7d71404a18ab51f07aaf563f02d2322a79d375`.
- New evaluation module: `tavern_ai/confirm_buy_s64405d5e.py`, commit `e40951ea3f3fa5308d2686c43f46b589b1af0444`.
- Statistical regression tests: `tests/test_confirm_buy_s64405d5e.py`, commit `7f123a72313a7c16aa2fb10a6b84b8d533456f1c`.
- Independent workflow: `.github/workflows/experiment-s-20261102-64405d5e-r002.yml`, experiment commit `9effe2d28d64530c1c67f630659b48702e68aaab`; subsequent trigger-path restriction `a3ff6e05b9f480c0782fd8251772d4028bb42a6c`.
- Policy algorithm source is unchanged, SHA256 `60592c03c965631d2227528529ee389b3bccfde4d21f76ee68dd03221ca7edbc`; R002 evaluator SHA256 `d10e681ec40408824a16e0d81e3fcd656197fd5dfb09ad7fd8640e3eae82bca1`.

## Run and environment confirmation
- **SUCCESS** [GitHub Actions #41417630541](https://github.com/sstxww/reinforcement-learning/actions/runs/41417630541): **27 unit tests passed**, verified pinned TavernGym source and patch, 41 true completed eight-seat games, 41 receipt integrity checks, and real evidence committed by the workflow.
- Result receipt commit: `671f31942bf8171b83f13d4908385f9a782a2440`.
- TavernGym version **1.1.0**, source hash `6d8712c93022ba11`, pinned upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; observe2 4017 float / 447 card index / 245 legal masked actions. Seat 0 controlled by the unmodified R001 candidate or original baseline, other seven seats official scripted bots.
- **PPO training steps 0** (this is a strategy / statistical validation round). No model/optimizer checkpoint. Original policy source is content-addressed by SHA256.
- Model SHA256 null, no Best promotion.

## Mandatory personal candidate match
- Seed **41100**, `Game.is_over() == True`, controlled rank **7**, placements **[7,4,6,3,8,1,2,5]**, **50** actions, **15** turns, 4 buy-before-play interventions. All mask-legal, combat truncations 0, turn-limit end false.
- Genuine receipt: `experiments/s-20261102-64405d5e/002-41100.json`.

## Held-out paired experiment, 20 unseen seeds
Seeds **41101–41120**, candidate and control each ran a separate full real eight-player game with the same seed. All forty finished normally.

- Baseline ranks: **[8,7,8,8,8,8,8,7,8,8,6,8,8,8,7,7,8,8,7,8]**.
- Candidate ranks: **[8,7,8,8,8,5,8,7,8,8,6,8,8,8,7,7,8,8,6,8]**.
- Baseline mean rank **7.65**, candidate mean rank **7.45**, paired candidate-minus-control **-0.20** (lower better).
- Candidate better in **2/20** cases, equal in **18/20**, worse in **0/20**.
- Seed **41106** changed rank from 8 to 5; seed **41119** from 7 to 6. All other paired placements equal.
- Candidate top-four **0/20**, baseline top-four **0/20**; first place **0/20** for both.
- **118** buy-first interventions across the 20 candidate matches. This policy is genuinely executed rather than an inactive flag.
- Nonparametric paired percentile bootstrap (4000 seeded resamples) 95% interval on mean placement difference: **[-0.55, 0.00]**. The interval includes 0, and almost all matches are near rank 8; the study does **not** establish competitive strength gain or justify promoting Best.
- All R002 receipts: `experiments/s-20261102-64405d5e/002-*.json` plus `experiments/s-20261102-64405d5e/controls/002-*.json`; metrics `reports/s-20261102-64405d5e/paired-002.json`.

## Cross-round interpretation
R001 used 6 pairs (12 games) and an additional independent candidate match; R002 used 20 fresh pairs (40 games) and an additional independent candidate match. **54 actual eight-seat matches**, **26 paired seeds**, total **160** candidate priority interventions. Across 26 pairs the candidate improved in 3 and tied in 23, no deterioration; total placement difference -5 across 26 pairs, **mean -0.1923**. Both candidates have 0 first-place and 0 top-four in paired tests. The measured difference is a small descriptive signal, not persuasive competitive evidence; avoid declaring a win.

## Failures, durability, and next hypothesis
- No code failure in the successful R002 workflow, so do not manufacture a failure report. R001 documented historical incidents from GitHub logs; those are not R002 failures.
- [R002 evidence Artifact #13128192372](https://github.com/sstxww/reinforcement-learning/actions/runs/41417630541/artifacts/13128192372) expires **2026-12-02 09:06 UTC**; permanent text receipts, metrics, code, and summary live in this branch. No neural checkpoint or permanent neural-model restore is claimed.
- A further large head-to-head study is not justified without policy-design changes: strong floor effects indicate more work is needed on card value, economy, and board quality. For a new hypothesis, measure hand/board resource signals and design an explicitly contextual replacement before spending another 40 games on this weak fixed priority.
- Review only after own final-head PR CI; do not merge other agent branches or promote this as Best.
