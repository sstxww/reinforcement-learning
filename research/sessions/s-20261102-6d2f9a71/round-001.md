# Round 001 — bounded MaskablePPO entropy ablation

- Session: `s-20261102-6d2f9a71`
- Branch: `agent/s-20261102-6d2f9a71/optimization-001`
- Starting `main` SHA: `6ac59235b8238196a0e6462de77b72413c829372`
- Successful experiment source SHA: `332fe14c252d97fc3f7fa75a2e8ffaa0c666a9da`
- Generated evidence commit: `a3ae791deb3b815e4f37eb9cf9f72d498c1d1e2a`
- GitHub run, **successful**: https://github.com/sstxww/reinforcement-learning/actions/runs/41413940695
- Initial **failed** run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413283468
- PR: to be linked in STATUS.md upon creation

## Existing knowledge and non-overlap

Read `README.md`, `AGENTS.md`, `docs/PROJECT_BACKGROUND.md`, `docs/SESSION_PROTOCOL.md`, `prompts/INDEPENDENT_SESSION.md`, `research/knowledge/README.md`, current open PRs #6 (baseline strategy), #7 (evaluation), #8 (infrastructure) and #9 (checkpoint/learning), and recent successful/failed Action runs. Starting `main` has no submitted session reports or reviewed knowledge proposals. Open PR findings are **unmerged leads**, not validated shared knowledge. This trial changes only new `tavern_ai/entropy_trial.py`, `tavern_ai/guarded_match.py`, a session-specific workflow, tests, and this session's evidence/docs. It does not touch common training, baseline, canary, CI or main workflow files.

## Falsifiable hypothesis and experiment

Changing only PPO entropy coefficient from 0.01 (reference) to 0.04 (candidate), with the same network, training seed and 256 training steps per arm, improves mean held-out placement against seven TavernGym scripted bots. Metric: candidate minus reference mean placement, where negative indicates improvement. Two paired held-out seeds (61001 and 61002), identical full-game runner, deterministic inference. Sample size is deliberately small and cannot prove competitiveness.

- Engine: pinned TavernGym **1.1.0**, verified source fingerprint `6d8712c93022ba11`, upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`
- Fixed patch SHA256: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`
- Observation contract: float32[4017] features, int32[447] cards, bool[245] legal mask
- Model: MaskablePPO MultiInputPolicy and TavernExtractor (256-d representation; 128-unit policy/value heads)
- Both arms: CPU, training seed 77331, 256 timesteps, n_steps=128, batch_size=64, n_epochs=4, gamma=.99, gae_lambda=.95, learning_rate=3e-4
- Resource limit: one GitHub Actions job with 85-minute timeout, 2 torch CPU threads, 30,000 game iterations maximum, 40 actions per turn maximum when end-turn is legal
- Reproduce: `python -m tavern_ai.entropy_trial --agent-id s-20261102-6d2f9a71 --train-seed 77331 --eval-seeds 61001 61002 --steps 256 --output-dir checkpoints/s-20261102-6d2f9a71` after `pip install -e '.[train,test]'` and `bash scripts/bootstrap_engine.sh`
- Exact isolated CI recipe: `.github/workflows/experiment-s-20261102-6d2f9a71.yml`

## First failed run and corrective change

Run #41413283468 successfully installed and verified the simulator, passed 14 unit tests, trained the first/reference arm for 256 steps, then **failed** on its first model-controlled game. The unbounded raw model repeatedly selected free actions until the canary safety limit was exceeded; **no valid receipt** was produced. That 256-step partial training was not retained as a recoverable checkpoint. The correction was a new isolated `guarded_match.py` real-game runner: keep action-mask enforcement, force legal end-turn after 40 actions within a turn, and delegate only mandatory non-end-turn choices to the existing BaselinePolicy. The shared `canary.py` was untouched.

## Successful training, actual full games, evidence

Run #41413940695 passed 14 tests, verified the fixed engine, trained both arms for **256 + 256 = 512 completed-run timesteps**, ran **4 complete eight-seat games** and committed receipts plus machine-readable metrics. Counting the unrecovered first run, logs show an additional 256 training steps before the failure: 768 executed in both attempts, but only 512 steps have preserved model checkpoints.

| Model | Seed 61001 rank / actions | Seed 61002 rank / actions | Mean rank | Top 4 | First |
| --- | --- | --- | ---: | ---: | ---: |
| Reference (ent_coef=.01) | 8 / 167 | 8 / 178 | 8.0 | 0/2 | 0/2 |
| Candidate (ent_coef=.04) | 8 / 167 | 8 / 178 | 8.0 | 0/2 | 0/2 |

All four completed with `Game.is_over()==True`; each full placements array is a permutation of 1..8. Seed 61001 placements: `[8,6,1,7,3,2,4,5]`; seed 61002: `[8,3,1,4,6,2,7,5]`. For each arm, forced legal end turns are 1 (61001) and 2 (61002); mandatory fallback choices=0, illegal actions=0, simulator combat truncations=0, turn-limit ends=false. See the raw JSON receipts, not a manually synthesized game record:

- `experiments/s-20261102-6d2f9a71/001-61001.json` — candidate, 61001, session's mandatory receipt
- `experiments/s-20261102-6d2f9a71/candidate-61002.json`
- `experiments/s-20261102-6d2f9a71/reference-61001.json`
- `experiments/s-20261102-6d2f9a71/reference-61002.json`
- `research/sessions/s-20261102-6d2f9a71/metrics-001.json` — exact machine-readable comparison

**Outcome:** candidate minus reference mean placement = **0.0**. Higher entropy did **not** improve observed placement under this very small training/evaluation budget. Both arms ranked last twice, making the experiment inconclusive about larger-scale learning. The safety-limit fix enables completed matches, but is not by itself a strength improvement. Do not present this as TavernArena ranking or Elo.

## Checkpoints, reproducibility, cleanup

Artifact: `entropy-s-20261102-6d2f9a71-41413940695`, https://github.com/sstxww/reinforcement-learning/actions/runs/41413940695 (Actions Artifacts). Includes two ZIPs, SHA256SUMS and four receipts; retention ends **2027-01-31**. No permanent model registry/backup is established.

- Reference ZIP SHA256: `28b36a7e669a2c1322817cdf802bab83538bb933cc16a401608c2c3cc21e56ed`
- Candidate ZIP SHA256: `4d0c4107a45522d298c9404c6e22b38ff6254fe76d64a5bb5c5fb14bbadc944e`
- Artifact archive SHA256: `b9fe13df0deb0d06c7bed2c41432eeb01ac25fb383699acca5fc9bf4c6194cbf`

To restore within retention: download the named Action artifact to `checkpoints/s-20261102-6d2f9a71/`, verify `sha256sum -c SHA256SUMS`, and use `--policy model --model <zip>` with the independent guarded runner; no resume-training metadata is provided by this one-shot ablation. Generated vendor files, pip caches, rollout data and ZIPs were excluded from Git. Only source, receipts, compact metrics and written research were committed.

## Reusable experience / next round

A fresh 256-step PPO policy may legally spin on no-cost actions without a per-turn end-turn budget; this is a correctness and simulation-completion failure, not an illegal-action failure. Budgeting and masked forced legal ending resolves it in this experiment. Two paired seeds with both ranks=8 cannot distinguish ent_coef .01 from .04; test longer 8k–32k+ training budgets and larger independent seed sets, measure action-type distributions and end-turn frequencies, and run a separate guarded-vs-unguarded regression suite before claiming any improvement. No ranked Arena play was attempted.
