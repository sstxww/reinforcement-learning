# s-20261102-1692601b status

- Branch agent/s-20261102-1692601b/optimization-001
- Main base 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Experiment code commit f0458b0bc357c83ee10306f798a2667cf91a6bca
- Real Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41422157901 SUCCESS
- Game version TavernGym 1.1.0, source hash 6d8712c93022ba11
- Training: finite 4-arm search on 10 true games, 0 neural/PPO gradient steps
- Full matches: 18, completed and validated; heldout [59131..59134] control ranks [8,7,8,7] and candidate [8,7,8,6], mean delta -0.25
- Candidate 10 sales, 0 orphan sales, 0 safety overrides; no top4/win gain
- Chosen rule: turn >=7, sell first slot once, then buy
- Weights: none; model_sha256 null. Source and selected parameters in metrics file are the durable small policy artifact.
- Receipt directory experiments/s-20261102-1692601b/; metrics research/sessions/s-20261102-1692601b/metrics.json
- Status RETEST pending formal review; PR/CI needs separate check
- Resume: bash scripts/bootstrap_engine.sh then python -m tavern_ai.sell_swap_1692601b --out-dir experiments/s-20261102-1692601b --metrics research/sessions/s-20261102-1692601b/metrics.json
