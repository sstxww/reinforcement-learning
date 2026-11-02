# Independent session status — s-20261102-1d9e7456

- Base SHA: main 6ac59235b8238196a0e6462de77b72413c829372.
- Current branch: agent/s-20261102-1d9e7456/optimization-001.
- Pull request: https://github.com/sstxww/reinforcement-learning/pull/14 (draft, integration review required).
- Code commit: 7682c75e30f5710ad4630487c3e6b87f7be083b6; workflow race fix: 1fdaf8ef998626517256be26172dda7cd3901b21; genuine evidence commit: 9d4125ae0b329adb2d27dd0c67741d276d863fdb.
- Real successful experiment workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41414297830.
- Actual training: six full real eight-seat calibration games, 355 agent decisions; zero PPO gradient steps. Tuned rule parameter is rightmost among multiple legal buy slots.
- Own full real match: seed 38200, engine TavernGym 1.1.0, own rank 5, placements [5,3,8,1,6,7,4,2], 54 agent decisions, valid and no truncation. Receipt: experiments/s-20261102-1d9e7456/001-38200.json.
- Held-out assessment: 3 paired seeds; baseline ranks [8,8,8], rightmost ranks [5,7,5], mean difference -2.33, top4 rates both zero. NOT proven strength gain.
- Best observed own rank across these matches: fifth, not first/fourth.
- Model checkpoint: research/sessions/s-20261102-1d9e7456/selected-policy.json (small JSON tuned rule choice, no neural weights). SHA256 22c6e04d3c389d23063066a4d5d97d13d9550d8c49b7a99fd2547a689503ee3f.
- Metrics with 12 raw match records: research/sessions/s-20261102-1d9e7456/metrics.json.
- Restore with Python 3.12, project dependencies, scripts/bootstrap_engine.sh, then run isolated script; for inference instantiate PurchasePolicy(selected_mode, seed) from the experiment script. Not a PPO policy.
- Artifacts expire in 90 days; model-selection JSON is also in Git and persistent subject to repository availability.
- Remaining gate: inspect PR CI after last docs commit. Do not merge until review; initial CI failed only because independent match receipt had not yet been committed.
- Next: increase evaluation to 20+ independent paired seeds, handle instrumentation for baseline buy opportunities, quantify variance and top-four performance.
