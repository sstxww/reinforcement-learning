# s-20261102-4d619f26 · Round 001 — public-observation teacher cloning

## Hypothesis and prior work
Main 315b068bac5ab6d8403c3c9b18f8c101c0cded5d. Main rules baseline and PPO both require gameplay skill evidence.
Other unmerged PRs target purchase/refresh/move/entropy; this experiment uses only isolated files.
Read docs/PROJECT_BACKGROUND.md, SESSION_PROTOCOL.md, CLOSED_LOOP.md,
and research/knowledge/INCIDENTS-20261102.md.

## Actual pinned engine mechanisms
TavernGym 1.1.0 / source hash 6d8712c93022ba11.
Upstream pinned actions.rs: Buy 8..15, Sell 16..22, Choose 30..45,
Play 46..125, Magnetize 126..195, Move 196..244.
Teacher labels are real legal Game.bot_action(0) outputs.
Student uses only 42 public own/global features and 245 legal mask elements;
it cannot read opponent hidden information or game RNG.

## Actual training and testing
Mask-aware MLP behavior cloning; epochs=8,
teacher matches=(61101, 61102, 61103, 61104), learner samples=451.
Supervised held-out seeds=(61211, 61212); examples=250,
exact action accuracy=0.4160, family accuracy=0.5480.
Train final minibatch loss=1.899003.
No PPO steps were run; total PPO timesteps = 0.
Candidate checkpoint hash SHA256=e46ecc54019df972c45755dea294794e302d51acdb57264c1f5d77180be3d1e7; restored successfully.
Model is an expiring Actions Artifact, not a permanent Champion.

## Genuine eight-seat independent matches
Paired seeds=(61421, 61422); seat 0 controlled by stated policy,
seven scripted TavernGym bots on all games. All receipts include placements and
action-family histograms. No research policy forced-end guard (count=0).
| Policy | Games | Seat-0 ranks | Mean rank | Top4 | First |
|---|---:|---|---:|---:|---:|
| clone | 2 | [8, 8] | 8.000 | 0.000 | 0.000 |
| baseline | 2 | [8, 7] | 7.500 | 0.000 | 0.000 |
| official_teacher | 2 | [7, 4] | 5.500 | 0.500 | 0.000 |
Mean paired clone minus baseline rank=+0.500.
Small sample: results are descriptive, not a strength proof; no Arena MMR inference.
Train/holdout/match seeds disjoint. Baseline and official teacher are separate policies.

## Result / promotion
RETEST: no statistical basis to declare strength improvement on n=2
paired seeds; do not promote. No automatic PR merge.

## Reproduction
python -m pytest tests/test_teacher_clone_s4d619f26.py
bash scripts/bootstrap_engine.sh
python -m tavern_ai.teacher_clone_s4d619f26 --out-dir experiments/s-20261102-4d619f26 --report-dir reports/s-20261102-4d619f26
Artifacts preserve candidate .pt for 30 days (if upload succeeded);
do not call this a durable model. The historical PRs are unmerged leads, not main facts.

## Next
Study why the public-only cloned policy disagrees with official teacher by action
family, especially shop card selection; validate source-derived card features before scaling PPO.
