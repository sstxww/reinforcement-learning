# Round 001 — purchase-slot selection under real TavernGym

Session: s-20261102-1d9e7456
Branch: agent/s-20261102-1d9e7456/optimization-001
Base main commit: 6ac59235b8238196a0e6462de77b72413c829372
PR: https://github.com/sstxww/reinforcement-learning/pull/14

## Hypothesis and boundaries

The V1 baseline chooses the first legal purchase action in slots 8..15. Seeded uniform purchase among multiple legal choices may reduce slot bias; rightmost is a directional ablation. Preserve every other BaselinePolicy action decision. Only isolated experiment script, tests, workflow and own session documentation were changed; no common runtime source nor shared train.yml changed.

Previously inspected main documents: README.md, AGENTS.md, docs/PROJECT_BACKGROUND.md, docs/SESSION_PROTOCOL.md, research/knowledge/README.md and research/sessions/ (no sessions on main at start). Open draft PR #6 works on strategy, #7 on evaluation, #8 on infrastructure, #9 on PPO; none of their claims was adopted as verified. Also inspected recent GitHub Actions success/failure and concurrent branch workflows. No shared file edits were made.

## Actual environment and implementation

Upstream pinned commit: fb61201a557ddd36a411cf44aac51ce4d9b606ce
Patch SHA256: 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0
Verified TavernGym 1.1.0 source hash: 6d8712c93022ba11
Contract: 4017 numerical features, 447 card indices, 245 legal-masked actions; number of card tokens: 3984.

Code: research/sessions/s-20261102-1d9e7456/run_purchase_ablation.py
Workflow: .github/workflows/experiment-s-20261102-1d9e7456.yml
Tests: tests/test_purchase_ablation_s_20261102_1d9e7456.py
Unit tests passed, including deterministic seeded choice and mask legality. PR initial CI: 15 unit tests passed; initial PR evidence gate correctly failed before the independently produced receipt existed. Do not mistake this failure for a simulator failure.

Run command after installing Python 3.12 project and pinned TavernGym: python research/sessions/s-20261102-1d9e7456/run_purchase_ablation.py
Hard bounds: 85-minute workflow timeout, 900-second per-game limit, 30000 outer iterations per game. Each match calls the actual Game(seed), observe2, legal_mask, bot_play, step, and reaches Game.is_over().

## Training and parameter choice (actual observed)

This is six complete real-game rule-parameter calibration episodes, NOT neural PPO gradient training; PPO timesteps = 0. Training seeds: [38100,38101] for each of baseline, uniform and rightmost. Actual training seat-zero decisions across six matches: 355. Select minimum calibration mean placement, baseline wins ties.

Calibration:
- baseline: seed ranks [8,6], mean 7.00, top4 0/2.
- uniform: seed ranks [7,7], mean 7.00, top4 0/2.
- rightmost: seed ranks [8,5], mean 6.50, top4 0/2.
Selected: rightmost. This is an exploratory model-selection outcome, not established strategy strength.

## Independent held-out evaluation (actual observed)

Held-out seeds: [38200,38201,38202], never used to choose mode.
- baseline ranks [8,8,8], mean 8.00, top4 0/3, first-place 0/3; total 119 controlled decisions.
- rightmost ranks [5,7,5], mean 5.6667, top4 0/3, first-place 0/3; total 157 controlled decisions.
- Mean rank difference: -2.3333 ranks (lower is better), n=3 paired seeds; NO claim of statistically proven improvement.
- Experimental rightmost had 45 opportunities with multiple legal purchase actions across held-out matches. Its mode made a different purchase-choice action every time. The baseline instrument records zero purchase opportunities because mode baseline bypasses opportunity counting; that zero does NOT mean it never had shop decisions.
- No illegal actions, protection truncations or turn-limit termination across recorded matches.

## Mandatory personally executed eight-seat match evidence

Receipt: experiments/s-20261102-1d9e7456/001-38200.json
Actual seat 0 rank 5, seed 38200, decisions 54, final turn 17, eight seats ranked [5,3,8,1,6,7,4,2], completed true, invalid moves 0, truncated combats 0, turn limit false. Other seven seats driven by official bots. This receipt is generated from Game.is_over() and validated by tavern_ai.validate_receipt, NOT manually manufactured. It is produced by this session's own uniquely named workflow and is distinct from shared PR CI's canary.

First real run https://github.com/sstxww/reinforcement-learning/actions/runs/41413891030 completed all simulation and uploaded the genuine evidence Artifact but the final git push was rejected (non-fast-forward because a session docs commit had advanced the same branch). No force push attempted. Fixed by fetching/rebasing the verified receipt commit onto the branch head; second run https://github.com/sstxww/reinforcement-learning/actions/runs/41414297830 succeeded in real simulation, validation, artifact upload and branch-only evidence commit 9d4125ae0b329adb2d27dd0c67741d276d863fdb.

## Evidence, checkpoint, limits and handoff

Raw receipts for all 12 completed matches and aggregate comparisons: research/sessions/s-20261102-1d9e7456/metrics.json.
Single independent canary receipt: experiments/s-20261102-1d9e7456/001-38200.json.
Small JSON rule-parameter checkpoint: research/sessions/s-20261102-1d9e7456/selected-policy.json.
Checkpoint SHA256: 22c6e04d3c389d23063066a4d5d97d13d9550d8c49b7a99fd2547a689503ee3f.
Restore by reading selected_mode=rightmost from the checked-in JSON and invoking PurchasePolicy(mode, game_seed) in the isolated script. No neural weights were produced or claimed. Both machine-readable records and checkpoint selection are preserved in Git; workflow Artifacts have 90-day retention and are NOT permanent weight storage.

No raw rollout files, caches, virtualenv or redundant model copies were committed. One three-game test set is too small for competitive conclusions; this may reflect favorable seeds. Uniform was not independently holdout-evaluated. Next round: 20+ independent paired held-out seeds, measure variance/CI and per-seed buy-choice opportunities, then consider incorporating findings through integrator review if replicated. Never change shared core baseline based on only three seeds.
