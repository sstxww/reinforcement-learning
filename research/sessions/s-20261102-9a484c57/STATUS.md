# AutoTavern-AI V2 independent session status

- Session: `s-20261102-9a484c57`
- Branch: `agent/s-20261102-9a484c57/optimization-001`
- Base main commit: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Current fixed-code commit: `8f98639e13234ce65ecd69a3dfb2c427160e16d3`
- Hypothesis: on scheduled tavern-upgrade turns, performing a legal tavern upgrade **before** optional hand play may improve scripted-bot placement versus original baseline ordering.
- Scope: only new `tavern_ai/upgrade_probe_9a484c57.py`, new tests, unique workflow and session-owned reports/receipts. Shared policy, training and eval untouched.
- Experiment status at writing: second dedicated Actions run in progress; unit-test step already passed, TavernGym bootstrap in progress. The first run failed before simulator setup owing to two mistaken test assertions; see `failures/001-baseline-action-order.md`.
- First run (failed): https://github.com/sstxww/reinforcement-learning/actions/runs/41415062300
- Current run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415219995
- Proposed seeds: 42021, 42022, 42023, baseline and early-upgrade arms, six complete eight-seat matches only if job finishes.
- PPO training steps: 0 (rule-policy ablation). No model checkpoint, no model Best promotion. Action budget: 55 seat-zero decisions per TavernGym turn; same for both arms.
- Model retention/recovery: not applicable to rule-only experiment; strategy recoverable from this Git branch. Game receipts will be recorded only upon real successful simulation, and then independently validated.
- PR: not yet created; must first obtain genuine complete-game receipts and summary.
- Next: inspect real job result; if failed, read exact job logs and make bounded root-cause fix; if passed, save empirical metrics, write proposal, open PR to main and check PR CI.
