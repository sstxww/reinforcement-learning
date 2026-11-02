# s-20261102-2b0d8089 — Status

- Round: 001 — **completed; negative reward-compression result**.
- Branch: `agent/s-20261102-2b0d8089/optimization-001`; base main `6ac59235b8238196a0e6462de77b72413c829372`.
- Run-head source commit: `ca47e15b45bf0b068fa4837f8da15f4927c27b76`.
- Receipt-only commit: `90c9eb41e713b1a180bf3d3835eb69b0acc7486b`.
- Pull request: [#21](https://github.com/sstxww/reinforcement-learning/pull/21), **draft**, awaiting PR-specific CI and integrator review.
- Successful run: https://github.com/sstxww/reinforcement-learning/actions/runs/41414058042
- Failed attempts: 41412952801 (model non-progress); 41413587545 (Python newline syntax).
- Steps: **512 on successful comparable run** (256/arm). Another 512 actually ran on the first failed attempt; cumulative work 1024.
- Held-out seeds: 27001 and 27002 (2 games per policy; six complete games).
- Best **observed** of tested policies: original rule baseline mean rank 6.5/8; raw PPO mean 7.5/8; signed-log PPO mean 8.0/8. No model strength gain verified; n=2.
- Aggregated metrics (not a game receipt): `research/sessions/s-20261102-2b0d8089/001-summary.json`, moved outside the CI receipt glob to avoid false failure; PR CI pending recheck.
- Mandatory real own-session receipt: `experiments/s-20261102-2b0d8089/001-27001.json` (rank 8; decisions 160; 8-rank array [8,2,1,5,6,4,3,7], safety pass count 6).
- Engine: TavernGym 1.1.0, hash `6d8712c93022ba11`, 4017/447 observations and 245 legal actions.
- Successful checkpoint archive: https://github.com/sstxww/reinforcement-learning/actions/runs/41414058042/artifacts/13126329809, 90-day GitHub Artifact, **expires 2027-01-31; no permanent backup**.
- Signed-log checkpoint SHA256: `2a23241582d8d1eb1313ee47dfb562bccef6d1e2a8e8cd956437b985a3014756`.
- Raw checkpoint SHA256: `30886ba44bb1067f533f80e89f0b15782fa0fa11de074a0191466efbbf6220f8`.
- Restore: `gh run download 41414058042 --repo sstxww/reinforcement-learning --name reward-s-20261102-2b0d8089-41414058042 --dir restored`, verify SHA, pinned engine before attempting `MaskablePPO.load`.
- Next: instrument per-iteration critic-loss variance and ≥20 paired held-out games after 2048+ steps per arm; avoid conflicts with PR #9 on `train.py` and `canary.py`.
