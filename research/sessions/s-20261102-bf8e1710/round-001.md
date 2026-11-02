# Round 001: proposed experiment (execution pending)

Hypothesis: Potential-based shaping of TavernGym's native sparse terminal
placement reward accelerates early MaskablePPO learning without changing the
discounted optimal policy.

Main base: 6ac59235b8238196a0e6462de77b72413c829372.
Prior evidence: upstream SoloEnv produces 0 on ordinary steps and terminal
rank reward. Main research/sessions contains no accepted rounds. Open draft
PRs #6-#9 work on unrelated baseline, training, evaluation and infrastructure.
No unmerged claims treated as confirmed.

New files: tavern_ai/reward_shaping.py, tavern_ai/reward_experiment.py,
tests/test_reward_shaping.py, session-owned GitHub Actions workflow.
Shared train.yml, train.py, baseline.py, CI, other branches are untouched.

Evaluation plan: paired training seed 33123, 256 actual PPO steps per arm,
full matches on held-out seeds 33011..33013 and mandatory separate model
game seed 33001. Log real receipts and statistics, not invented evidence.
Training step count at preparation: 0. Model checkpoint: not yet generated.

Results will be replaced from authentic completed runner execution.
