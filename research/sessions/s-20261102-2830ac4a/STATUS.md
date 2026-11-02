# Session s-20261102-2830ac4a — STATUS

- **Round:** 001 — completed real-game experiment; negative/inconclusive rank result, awaiting PR CI gate/integrator review.
- **Branch:** `agent/s-20261102-2830ac4a/optimization-001`; base main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **Research focus:** opt-in no-auto-sell baseline strategy, leaves original baseline and model untouched.
- **Actual execution:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415008425 (success), code SHA `f6cd60f951be78c67e30c6a717e5d600b05d49d8`.
- **Engine:** pinned TavernGym 1.1.0; source hash `6d8712c93022ba11`; `observe2` 4017/447/245; real eight-seat game.
- **Tests:** unit/regression tests passed; contracts and all seven receipts validated in Actions.
- **Training:** 0 PPO timesteps (pure rule policy), no model checkpoint, no restored optimizer, no Best model.
- **Required personal full-game evidence:** `experiments/s-20261102-2830ac4a/001-34200.json`; seed 34200, rank 8, 44 decisions, placements [8,5,7,1,3,6,4,2], 15 turns, complete, no guard or invalid actions.
- **Held-out evaluation:** candidate 3 games placements [7,8,8], mean 7.6667, first 0%, top-four 0%; same-seed unchanged baseline exactly [7,8,8], mean 7.6667, first 0%, top-four 0%. Difference 0.00, inconclusive.
- **Summary:** `reports/s-20261102-2830ac4a/hold-sell-paired.json`; seven genuine completed match receipts retained in session directory.
- **Candidate policy SHA256:** `0fbedc281a33e4ff5f7c52ddb22e2290db7193c055b1a85f1cccb72c260c481f`.
- **Artifact:** `hold-sell-s-20261102-2830ac4a-41415008425`, artifact ID `13127795190`, expires 2026-12-02 08:44:36 UTC. Git-tracked JSON receipts and code survive artifact expiry, but no weights exist.
- **Failures:** none in own workflow. Another PR's `sb3_contrib` missing-module CI issue is outside this branch and not modified.
- **Next hypothesis:** measure observed action divergence and legal sell availability before spending additional optimization budget; unchanged placements alone do not show strategy exposure.
- **PR:** to be created for main, draft until own latest-head CI passes.
