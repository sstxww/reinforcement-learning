# Round 001 — bounded shop refresh experiment

- Session: `s-20261102-6cc5d763`
- Own branch: `agent/s-20261102-6cc5d763/optimization-001`
- Base main SHA: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Hypothesis: when the original baseline would end the turn with no legal Buy actions, one legal Refresh (action 1) can improve rank without introducing pathological loops.
- Verified upstream action layout: TavernGym `actions.rs` maps EndTurn=0, Refresh=1, Buy=8..16.
- Avoids overlapping ongoing PRs on reward, entropy, card embedding, buy-slot bias, and play positioning. The only policy source modified is the new `tavern_ai/refresh_ablation.py`.
- Engine contract: TavernGym 1.1.0, source hash `6d8712c93022ba11`, observe2 (4017 float, 447 card slots), 245 masked actions.
- Strategy tuning, **PPO steps 0**; no newly trained checkpoint.
- Experiment plan: candidate must complete seed 36501, then baseline and candidate each run seeds 36502–36504; total 7 real complete eight-seat matches if all finish. Every action checked against native legal mask.
- Candidate restriction: max one refresh per turn, no refresh before turn 3, no refresh when a Buy action is legal, no refresh when action budget >=80, original baseline decisions otherwise.
- Expected data: `experiments/s-20261102-6cc5d763/001-36501.json`, paired receipts, and `reports/s-20261102-6cc5d763/comparison.json`.
- Action workflow: `.github/workflows/experiment-s-20261102-6cc5d763.yml` only on own branch, one finite job (75 min timeout), no recursive writes.
- Actual run, seeds, full-game status, illegal actions, ranks and statistics: **NOT YET VERIFIED** at initial commit. Populate only from real execution.
- Existing evidence: PR #15 reports 1280-step PPO continuation without improvement in four games; PR #18 card pooling, #17 input scaling and #16 entropy reported no improvement at tiny budgets.
- Best model: no new model; no promotion. Candidate conclusions remain provisional unless independently evaluated.
- Next: read actual Actions logs, fix any failure, write observed metrics and PR link, then decide whether to vary refresh threshold.
