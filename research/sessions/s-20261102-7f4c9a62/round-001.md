# Round 001 — isolated MaskablePPO entropy probe

## Session, base and source
- SESSION_ID: s-20261102-7f4c9a62
- Independent branch: agent/s-20261102-7f4c9a62/optimization-001
- Base main commit: 6ac59235b8238196a0e6462de77b72413c829372
- Experiment implementation commit: e4af555a2f6687765988b4d2ae7a118a728ba1f3
- GitHub Actions generated genuine receipts commit: 23f3b298ababea09c294b31a101a43f56b6f3534
- Real experiment run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413477918 (success)
- PR: https://github.com/sstxww/reinforcement-learning/pull/16 (draft; no main merge attempted).

## Research hypothesis
Under equal initial seeds, environments and 128-step PPO budgets, action-masked entropy coefficient 0.02 may improve exploration and thus mean placement relative to coefficient 0.0. This is an exploratory smoke experiment, NOT an adequacy claim about 128-step training. Lower mean placement is better.

## Prior experience reviewed and conflict avoidance
Read README.md, AGENTS.md, docs/PROJECT_BACKGROUND.md, docs/SESSION_PROTOCOL.md, research/knowledge/README.md, and research/sessions/ on main. Main's session and proposal directories contained only placeholders; no integrated or replicated training-effect conclusion existed at the start.

Read current four PRs and their changed-file lists:
- #6: baseline economy strategy (unmerged draft); avoid baseline.py.
- #7: seeded evaluation (unmerged draft); avoid evaluate.py.
- #8: infrastructure/receipt/storage (unmerged draft); avoid validator and shared workflows.
- #9: PPO/resumable checkpoints (unmerged draft); avoid train.py and canary.py.
These are unmerged research leads, not established strength results.

## Isolated source and setup
Changed ONLY new session-specific files: tavern_ai/entropy_probe.py, tests/test_entropy_probe.py, and .github/workflows/experiment-s-20261102-7f4c9a62.yml; generated receipts and this session's reports. No main, upstream, shared train.yml or other branch changed.

- Real patched TavernGym: version 1.1.0; source hash 6d8712c93022ba11.
- Pinned upstream commit: fb61201a557ddd36a411cf44aac51ce4d9b606ce.
- Patch SHA256: 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
- Engine observe2: 4017 float features, 447 integer card slots, 245 legal-mask actions, 3984-card catalog.
- Script confirmed engine contract before starting and canary confirmed dimensions and legal actions on every decision.
- Independent CPU Actions runner; workflow timeout 75 minutes; torch threads=2.
- Reproduce: after installing train/test deps and bootstrapping engine, run
  python -m tavern_ai.entropy_probe --session-id s-20261102-7f4c9a62 --steps 128 --train-seed 70141 --start-seed 31041 --games 2 --base-sha 6ac59235b8238196a0e6462de77b72413c829372

## Real training
Two independent MaskablePPO MultiInputPolicy networks trained with identical train seed 70141:
- A (zero): ent_coef=0.00, 128 actual PPO timesteps.
- B (regularized): ent_coef=0.02, 128 actual PPO timesteps.
- Total real steps: 256. No resumed weights. n_steps=128, batch_size=64, n_epochs=4, learning_rate=0.0003, gamma=0.99, gae_lambda=0.95, device=CPU.
- Observations and legal masks come from the actual patched game engine, not fabricated arrays. Single training environment versus scripted opponents.
- Both checkpoints saved only as the isolated Actions Artifact entropy-s-20261102-7f4c9a62-41413477918 with 30-day retention, expires 2026-12-02 UTC; NOT durable storage.
- Zero model: checkpoints/s-20261102-7f4c9a62/zero/model.zip SHA256 6c0f145d1e96cc878ebc729d59567e90a44548deacfcac53c82827a8e94d2ae1.
- Regularized model: checkpoints/s-20261102-7f4c9a62/regularized/model.zip SHA256 a31b0098abc1f285a7aa11b9ada9c827c9d2ba319666f60324a7153315ca6d9f.
- Metadata JSONs are included in Artifact, with observed source fingerprint, seeds and step counts.
- To restore while Artifact exists, download the named Artifact from run 41413477918, verify model SHA256, install the same pinned engine and training dependencies, then load model.zip with MaskablePPO on CPU. Do NOT silently resume on changed catalog.

## Genuine complete eight-seat TavernGym matches
Same held-out game seeds 31041, 31042 for all three arms; each single-seat policy controlled seat 0, the other seven seats used engine.bot_play. The canary loop terminated only when Game.is_over() was true. All six JSON receipts are under experiments/s-20261102-7f4c9a62/.

Mandatory personally initiated match receipt:
- experiments/s-20261102-7f4c9a62/001-31041.json
- policy: trained regularized entropy-PPO, seed 31041, turn 14, seat-0 decisions 153.
- placements by seat: [8, 5, 6, 4, 1, 7, 3, 2].
- completed true, truncated_combats 0, turn_limit_end false; mask checks detected zero illegal selected actions.
- Engine fingerprint, policy version, training seed, training steps and model hash included in receipt.

Paired held-out results (two independent game seeds per arm):
| Arm | Seat 0 ranks | Mean rank | Top 4 rate | First rate | Seat 0 decisions |
| --- | --- | ---: | ---: | ---: | --- |
| Unmodified baseline | 8, 6 | 7.0 | 0/2 | 0/2 | 84, 96 |
| PPO ent_coef=0.0 | 8, 8 | 8.0 | 0/2 | 0/2 | 153, 101 |
| PPO ent_coef=0.02 | 8, 8 | 8.0 | 0/2 | 0/2 | 153, 101 |

Primary machine-readable report: reports/s-20261102-7f4c9a62/entropy-comparison.json.
Unit tests and training/full-game/Artifact/receipt-commit steps all succeeded in Actions 41413477918. Match validation rejects incomplete games, illegal masks before stepping, and game truncation.

## Interpretation, negative findings, limitations
Observed rank difference regularized minus zero = 0.0 (no advantage). Both early PPO checkpoints returned eighth place twice, worse than the baseline on this particular two-seed sample. Identical ranks and decision counts across PPO variants do NOT prove that action sequences or resulting game states were identical; no action trace was saved.
There is NO evidence that 0.02 improves competitive strength, and the sample is far too small for a statistically supported degradation claim either. The tiny training budget likely undertrains both networks; this is a candidate explanation, not a demonstrated cause. No Arena practice or ranked games, Elo or independent self-play were performed.

## Reuse and next round
- Successful technique: isolate experiments by branch, directory, workflow, seed and Artifact, and commit exact engine-backed game receipts.
- Not successful as strength improvement: 128 steps with either entropy coefficient; do not promote the checkpoints.
- Potential failure mechanisms: very short rollout budget, uninformative optimization progress, script-bot distribution.
- Next hypothesis: increase each model to at least 2048 steps, evaluate paired >=20 held-out seeds and multiple training seeds, report confidence intervals and cost per step; inspect action distributions for genuine entropy effects.
- Cleanup: no weights, rollout logs, caches or virtual environments committed. Do not delete the sole Artifact until recovered; Git has only SHA256 and resumable metadata index, not weights.
