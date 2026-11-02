# Round 001 — Post-purchase bounded sale ablation (completed, negative pilot)

Session ID: s-20261102-2d73e890
Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
Branch: agent/s-20261102-2d73e890/optimization-001
Execution: https://github.com/sstxww/reinforcement-learning/actions/runs/41422154307 (success)
Result commit: 9e3620fbd8e7d2e7e553bc71005b935619de1995
Engine: TavernGym 1.1.0, source hash 6d8712c93022ba11
Observe2 contract: 4017 features, 447 card slots, 245 actions, 3984 cards
Upstream pinned source: fb61201a557ddd36a411cf44aac51ce4d9b606ce
Model: none; actual neural PPO gradient steps = 0; no model weights/checkpoints
Algorithm: rule-policy parameter selection via complete-game rank, not PPO or BC

## Inherited evidence and rationale
Merged BaselinePolicy prioritizes choice 30..45, play 46..125, magnetize 126..195, upgrade and buy 8..15, but never voluntarily chooses sell 16..22. Upstream docs/TAVERNGYM.md confirms the action mapping. Public knowledge INCID­ENTS-20261102.md records PPO full-game timeout/Release permission issues. Open parallel PRs pursue BC, Freeze, hero-power, opening upgrades and seating; this study edits only unique policy/tests/workflow/session paths.

Test hypothesis: a purchased card blocked from playing could justify selling a board unit to create space. Counter-hypothesis: selling without card value or warband synergy awareness destroys long-term board power.

## Implementation and mechanism checks
- New sell_cycle_2d73e890.py delegates baseline except when a same-turn purchase remains unplayable/non-magnetizable; mandatory choice outranks sale.
- Strictly public 245-bit action mask plus local turn/action count. No hidden opponent data, RNG or future observations.
- Sale capped to 1 or 2 per turn. Inherited baseline 85-action forced end counted as a safety guard, not learned competence.
- Seven tests cover buy-to-sell, premature/double-sell prevention, pending choice and magnetize, turn reset, mask rejection, zero-budget equivalence and safety behavior.
- GitHub Actions tests and real pinned engine bootstrap passed.

## Actual bounded tuning
Train seeds: 68310, 68311, 68312, 68313, each full 8-seat TavernGym game for budgets 0,1,2 (12 games).
- Baseline budget0 placements [8,7,8,8], mean 7.75, no top4.
- Budget1 placements [8,7,8,8], mean 7.75, mean 3.25 sells/game.
- Budget2 placements [8,8,8,6], mean 7.50, mean 4.75 sells/game.
Choice frozen from training only: budget2.

## Genuine independent comparison
Eight heldout paired seeds: 68410..68417. 16 further complete eight-seat TavernGym games (total 28).
- Baseline placements [8,6,6,7,8,2,7,7]; mean 6.375, top4 1/8 (12.5%), first 0/8, mean sales 0.
- Budget2 placements [7,8,5,8,7,8,6,7]; mean 7.000, top4 0/8, first 0/8, mean sales 5.75.
- Per-seed candidate minus baseline rank: [-1,2,-1,1,-1,6,-1,0]; mean +0.625 (positive = WORSE). Descriptive 95% Student-t CI about [-1.42,+2.67]; small n and skew make it weak.
- All games completed, illegal policy actions 0 (runtime enforces mask); engine truncated combats 0, turn limit 0 and safety forced ends 0. Every candidate receipt has game placements, engine hash, seed, turns, decisions, sales and code commit.
- Results: reports/s-20261102-2d73e890/001-summary.json and experiments/s-20261102-2d73e890/001-68410.json .. 001-68417.json.
- Full job URL above; all steps success including receipt persistence. No model SHA256/checkpoint since no model was trained.

## Interpretation and integration
REJECT this exact unconditional first-legal-minion sale mechanism as a *performance candidate*: heldout rank worsened and no top4. Do not generalize this to all possible value-aware selling; eight seeds are insufficient. Protect shared main/Champion; no promotion. Keep only isolated test mechanism, negative trial data and reviewable PR as research knowledge, not as default policy. Public release candidate weights are not altered.

## Faults and continuation
No execution faults. No failed jobs to retry. Most valuable next experiment: use publicly visible card statistics/effect metadata and public board to score the incremental value of a purchase before selling; compare against the original baseline with separate seeds and more games. Continue only if there is a reproducible positive signal. Avoid another naked PPO-step increase.

## Reproduction
bash scripts/bootstrap_engine.sh
python -m pytest tests/test_sell_cycle_2d73e890.py
python -m tavern_ai.sell_cycle_experiment_2d73e890

The experiment uses 12 training-seed games to select an integer parameter and then 16 untouched holdout games. No Arena matches, no long-running jobs, no oversized raw rollout.
