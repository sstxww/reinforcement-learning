# STATUS — s-20261102-6d2f9a71

- Session ID: `s-20261102-6d2f9a71`
- Exclusive branch: `agent/s-20261102-6d2f9a71/optimization-001`
- Parent main commit at session start: `6ac59235b8238196a0e6462de77b72413c829372`
- Experiment code SHA: `332fe14c252d97fc3f7fa75a2e8ffaa0c666a9da`
- Evidence commit: `a3ae791deb3b815e4f37eb9cf9f72d498c1d1e2a`
- PR: https://github.com/sstxww/reinforcement-learning/pull/20 (draft, integration review required)
- Status: **completed exploratory round, no proven strength gain**
- Successful GitHub run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413940695
- First failed run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413283468 (raw model exceeded game loop cap)
- Actual training: **512 saved training steps** (256/reference and 256/candidate); additional 256 unsaved steps in first failed attempt; aggregate actual executed steps **768**
- Full real eight-player games: **4/4** completed in successful run, each with seven official scripted opponents
- Best validated placement: **8th** (reference 2/2, candidate 2/2); mean=8.0 for each arm; top4=0%, first=0%; neither configuration demonstrated a benefit
- Held-out evaluation seeds: 61001 and 61002 (paired)
- Own mandatory receipt: `experiments/s-20261102-6d2f9a71/001-61001.json`; seat0 rank 8, decisions 167, turns 18, placements `[8,6,1,7,3,2,4,5]`; zero illegal actions/truncations
- Metrics: `research/sessions/s-20261102-6d2f9a71/metrics-001.json`
- Report: `research/sessions/s-20261102-6d2f9a71/round-001.md`
- Shared proposal: `research/knowledge/proposals/s-20261102-6d2f9a71-001.md`

## Model checkpoints and restart

Artifact name: `entropy-s-20261102-6d2f9a71-41413940695` under run https://github.com/sstxww/reinforcement-learning/actions/runs/41413940695 ; expires on **2027-01-31**. **Not permanently stored.** No external registry or long-lived training state.

- `checkpoints/s-20261102-6d2f9a71/reference.zip`: SHA256 `28b36a7e669a2c1322817cdf802bab83538bb933cc16a401608c2c3cc21e56ed`
- `checkpoints/s-20261102-6d2f9a71/candidate.zip`: SHA256 `4d0c4107a45522d298c9404c6e22b38ff6254fe76d64a5bb5c5fb14bbadc944e`

Download artifact files while available, verify `sha256sum -c SHA256SUMS`, bootstrap TavernGym using `bash scripts/bootstrap_engine.sh`, and use `tavern_ai.guarded_match.run(seed,agent_id,policy="model",model_path="<zip>")` for a complete game. To re-train from scratch, rerun `python -m tavern_ai.entropy_trial --agent-id s-20261102-6d2f9a71 --train-seed 77331 --eval-seeds 61001 61002 --steps 256 --output-dir checkpoints/s-20261102-6d2f9a71`.

## Next round candidate

Investigate why both 256-step policies terminate last against scripted bots; instrument action usage and end-turn frequency, then compare one longer bounded PPO training budget and at least 8 independent evaluation seeds. Check `main` and open PRs again before starting. Keep all subsequent experiments in this session's branch/owned paths and do not alter shared training infrastructure.
