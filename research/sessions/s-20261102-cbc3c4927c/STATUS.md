# STATUS — s-20261102-cbc3c4927c

- Round: 001 completed, awaiting PR CI review
- Branch: `agent/s-20261102-cbc3c4927c/optimization-001`
- Base: `6ac59235b8238196a0e6462de77b72413c829372`
- PR: [#22](https://github.com/sstxww/reinforcement-learning/pull/22) (draft; final CI review pending)
- Code: factorized card encoder + masked legal end-turn safety experiment; isolated tests/workflow
- Training: two real independent runs of 128 timesteps = 256 timesteps executed; final saved PPO was trained for 128 timesteps (not resumed)
- Failed attempt: [Actions 41413377072](https://github.com/sstxww/reinforcement-learning/actions/runs/41413377072), unguarded PPO game hit loop safety limit
- Successful verified run: [Actions 41414184717](https://github.com/sstxww/reinforcement-learning/actions/runs/41414184717)
- Complete baseline receipt: `experiments/s-20261102-cbc3c4927c/001-baseline-22022.json`, seed 22022, rank6, 59 decisions, all placements [6,7,5,3,2,8,1,4]
- Complete model receipt: `experiments/s-20261102-cbc3c4927c/001-22022.json`, seed 22022, rank8, 311 decisions, all placements [8,4,5,6,7,3,2,1]; game.is_over=True, 4 legal end-turn interventions, 0 combat truncations
- Measured card parameters: 458,112 -> 237,376 (-48.18%); CPU forward batch16 median 0.687101ms -> 0.608044ms
- Best validated model match result: seat0 rank8 on n=1; no strength improvement established
- Checkpoint: [artifact 13126448465](https://github.com/sstxww/reinforcement-learning/actions/runs/41414184717/artifacts/13126448465), expires 2027-01-31; NOT permanently archived
- Model SHA256: `2f06972140a40bf04cca6321c5a70198b69d7e60775980e4801f6578df871508`. Restore by downloading artifact, verify checksum, ensure engine/metadata match, then pass `--resume` in train.py. Artifact expires; rerun from seed if unavailable.
- Compact summary: `reports/s-20261102-cbc3c4927c/001-summary.json`
- Next: check PR CI, compare old vs new architecture with paired budgets and >=10 held-out matches, reduce forced end-turn interventions.
