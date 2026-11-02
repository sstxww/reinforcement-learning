# STATUS — Session s-20261102-14ce98f3

- Branch: `agent/s-20261102-14ce98f3/optimization-001`; base main `6ac59235b8238196a0e6462de77b72413c829372`.
- Original run: [#41413148710](https://github.com/sstxww/reinforcement-learning/actions/runs/41413148710) — **failure in uncapped model evaluation**; tests, engine verification, 1 independent complete baseline match and both PPO training arms succeeded.
- Actual training: 256 original-reward + 256 scaled-reward = **512 PPO timesteps** (verified in model training metrics).
- Real complete match: `experiments/s-20261102-14ce98f3/001-26011.json`, seed 26011, 8 players, placements `[8,6,4,2,5,7,1,3]`, rank 8, 39 seat-0 decisions, 14 turns, no simulator truncation.
- No verified model rank yet. Uncapped scaled model seed 26012 hit 30,000-iteration safety limit; not a completed match.
- Metrics: `experiments/s-20261102-14ce98f3/metrics/raw.json` and `scaled.json`. Last logged value loss same (0.51085542), no observed benefit.
- Recovery evaluation: `.github/workflows/reward-recovery-s-20261102-14ce98f3.yml`, evaluates separately labeled guarded models (18 max actions per turn, records forced legal endings).
- Checkpoint artifact: [reward-models-s-20261102-14ce98f3, run #41413148710](https://github.com/sstxww/reinforcement-learning/actions/runs/41413148710/artifacts/13127120696), expires **2026-12-02**; not permanent. Raw SHA256 `6b086172e7d08a7d19fa64ab67034193e6f340c4c64078eff3f941c1e369679d`; scaled SHA256 `95224bd6c3c4e406255d30718a702f1d1be95fb0e8e7c90974d82ef42c19ec0e`. To restore, download artifact, verify both hashes, run `python -m tavern_ai.reward_eval --agent-id s-20261102-14ce98f3 --model checkpoints/s-20261102-14ce98f3/scaled.zip --seed 26012 --receipt experiments/s-20261102-14ce98f3/002-26012.json`.
- PR: not yet created; to be opened after verification of recovery match receipts.
- Next: inspect recovered model play, classify interventions, repeat independent paired seeds if possible, avoid claiming strength improvement from one game.
