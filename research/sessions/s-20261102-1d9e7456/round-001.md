# Round 001 — purchase-slot selection under real TavernGym

Session: s-20261102-1d9e7456
Branch: agent/s-20261102-1d9e7456/optimization-001
Base main commit: 6ac59235b8238196a0e6462de77b72413c829372

## Research hypothesis
The V1 deterministic baseline always buys the first legal shop slot. Breaking first-slot bias using a per-game seeded uniform draw among buy actions 8–15 may improve mean final placement. A rightmost action is a contrasting ablation. Keep all other baseline decisions unchanged.

## Previous research and concurrent boundaries
Main research knowledge README contains no promoted verified conclusions. Open draft PR #6 studies economy/strategy, #7 evaluation, #8 infrastructure, #9 resumable PPO. Other session workflows currently study reward/card architecture/placement. None of these draft claims is treated as verified. This session modifies no common runtime modules, no shared train.yml, and no other session results.

## Protocol and reproducibility
TavernGym pinned upstream commit fb61201a557ddd36a411cf44aac51ce4d9b606ce.
Pinned patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
Required engine version 1.1.0, source hash 6d8712c93022ba11; observation 4017 float features, 447 card IDs, 245 masked actions.

Distinct, bounded workflow: .github/workflows/experiment-s-20261102-1d9e7456.yml.
Experiment source: research/sessions/s-20261102-1d9e7456/run_purchase_ablation.py.
Python 3.12, install project test dependencies and bootstrap pinned TavernGym, then run the script.
Training calibration: real eight-seat matches on seeds 38100 and 38101 per baseline, uniform and rightmost (6 matches). Choose minimum mean rank with baseline winning ties. Training uses rule-parameter tuning rather than gradient reinforcement learning (PPO steps = 0). Actual game decisions and model selection are saved by the job.
Independent holdout: seeds 38200, 38201, 38202, baseline against selected mode (3 or 6 games). Games require Game.is_over(), complete 8-seat placement permutation, valid action masks, zero invalid actions and zero protection truncations. Each match has a 900-second wall limit; workflow job has 85-minute limit.

## Evidence status
Initial draft at commit 7682c75e30f5710ad4630487c3e6b87f7be083b6: source and isolated workflow committed; NO real game or tuning results verified yet. Do not infer performance improvement from any planned experiment.
Real receipt expected at experiments/s-20261102-1d9e7456/001-38200.json.
All raw training and holdout game receipts and paired metrics expected at research/sessions/s-20261102-1d9e7456/metrics.json.
Small rule-choice checkpoint expected at research/sessions/s-20261102-1d9e7456/selected-policy.json, SHA256 recorded in metrics; no neural model weights.
Action Artifact retention: 90 days and not durable storage of model weights. The small selected rule JSON is intended for Git.

## Next research hypothesis
After inspecting completed results, if multiple legal buy choices almost never occur, pivot to an action range with measurable opportunity count. Otherwise increase paired heldout seeds and report confidence intervals. Never claim significant strength gain from only three matches.
