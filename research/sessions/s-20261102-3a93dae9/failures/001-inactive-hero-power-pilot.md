# Failure 001 — Pilot produced no hero-power actions

failure_signature: zero experimental interventions
run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415703877
source_SHA: 7bb35feeb222bf05aefc5bc0615db74ec130b3d4
seeds: 18021, 18022
actual_result: complete candidate eight-seat matches rank [8,8], action count [42,47], hero-power use [0,0], game_is_over true, no truncation/invalid action.
root_cause: zero-cost-only activation restriction left no opportunities in sampled seeds; identical rank to baseline cannot be used to infer policy effect.
fix: accept a legal hero power from turn 3 when price <=3 gold and >=3 gold is reserved. Instrument available hero-power turns and successful hero actions.
verification: https://github.com/sstxww/reinforcement-learning/actions/runs/41416155846 (SUCCESS; 37 hero-power activations in six paired real games).
status: repaired intervention coverage, not a claim of competitive gain.
