# Experiment feasibility failure: zero refresh activations (Round 001)

- Signature: `zero-policy-interventions` (not a Python/CI/runtime crash).
- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415018609 / job 125176644550.
- Source SHA: `d1eed5699186a265d8c704bb7eaea917dec29535`.
- Seeds: 36501–36504.
- Observed outcome: all candidate games completed, but `refreshes_chosen=0` for each one. Equal baseline/candidate ranks [8,8,8] on paired seeds.
- Reproduce with pinned TavernGym and `python -m tavern_ai.refresh_ablation --seed 36501 --start-seed 36502 --games 3`.
- Root cause at selection level: the conjunction `baseline_action == EndTurn && Refresh legal && no Buy legal && turn>=3` did not hold in these games; likely no legal refresh once buying is unaffordable, but exact state-frequency cause is not instrumented and remains unproven.
- Repair recommendation: define a distinct R002 hypothesis under which the candidate can refresh *instead of* a legal purchase when both are legal; add unit test for the new branch and require an activation counter >0 before interpreting competitive metrics.
- Validation: the original code's unit tests, real engine, and seven completed games all passed; original hypothesis **not empirically activated**, not a gameplay strength failure.
- No blind retry of identical SHA/seed; no extra CI resources consumed for the same condition.
