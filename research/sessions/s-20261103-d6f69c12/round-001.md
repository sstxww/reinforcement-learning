# Round 001 — correct raw PPO action taxonomy

## Reproducible source finding
- Branch base: `df07dd23c99079449417fa8e645cf2b6c76b9704`, session `s-20261103-d6f69c12`, engine TavernGym 1.1.0 source hash `6d8712c93022ba11`, 4017 floats / 447 cards / 245 actions.
- On this main snapshot, `tavern_ai.behavior_audit_v5_880b8a71.category()` grouped actions 1 (Refresh) and 2 (Freeze) as `other`, grouped SELL and ACTIVATE together, and also marked MAGNETIZE and MOVE as `other`.
- Verified source-of-truth: `tavern_ai.mechanics_audit_f3af3b4d.ACTION_FAMILIES`, which independently checks all 245 runtime `taverngym.action_name()` prefixes in its pinned-engine mechanics tests. For example, action 1=Refresh, 2=Freeze, 7=Cancel, 196–244=Move.
- Impact: aggregate `other` bins hid the very Refresh/Freeze/Move family distributions needed to investigate rank-eight model loops. This is an **instrumentation bug**, not proof the underlying policy is defective because of the audit code.

## Actual implementation
- Reuse the existing verified action-family source instead of hardcoding a second conflicting mapping. Keep `end_turn` for existing report consumers.
- Add `raw_action_category_counts` and `raw_choice_when_buy_legal` alongside already present executed-action / guard counters. This prevents forced END_TURN from overwriting the model's intended action distribution.
- Add offline, synthetic boundary and out-of-range tests; update existing action 244 test.
- Reproduction (on checked-out branch): `python -m pytest -q tests/test_behavior_audit_v5_880b8a71.py tests/test_action_taxonomy_s_20261103_d6f69c12.py`.
- Actual proof: [Actions #41509611319](https://github.com/sstxww/reinforcement-learning/actions/runs/41509611319) ran offline regression checks, pinned engine bootstrapping and runtime source action-name audit successfully; the genuine eight-seat baseline seed 93471 finished rank 6, 16 turns, 47 decisions, placements [6,4,7,3,2,5,8,1], zero truncated combats, no turn limit. Original Artifact [#13172837469](https://github.com/sstxww/reinforcement-learning/actions/runs/41509611319/artifacts/13172837469) was downloaded and the faithful JSON content is committed to `experiments/s-20261103-d6f69c12/001-93471.json`. The baseline match verifies infrastructure only, not PPO improvement. Final workflow conclusion remains to be checked.

## Evidence and limitations
- Main report `reports/s-20261102-83d91476/001-buy-opportunity-report.json` cites real Actions #41428098018: V2 in two completed games ranked [8,8], had **74 BUY-mask-legal decision exposures and zero BUY**, and 222/248 raw actions were IDs 1 or 2. Baseline in the same seeds bought 33 times with 48 legal-buy exposures and ranked [6,7]. This is genuine observational evidence, not causal proof.
- The canonical unpromoted 1408-step candidate has paired heldout ranks [8,8,8] vs baseline [6,8,8], with no Champion. Other draft ablations reporting forced BUY without rank gain caution against a single-factor explanation.
- This round makes **0 PPO updates**, **0 new model checksums**, **0 Champion promotions**, no ranked Arena entry. Changing diagnostics cannot alone show a better final rank. Do not mix guarded actions with raw policy statistics.
- Pending gates are real TavernGym execution, final-head PR CI, careful current-main integration review and an independent behavior evaluation after any future training fix.
