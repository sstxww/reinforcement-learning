# Session s-20261102-bedfc382 — Round 001

- **Base main commit:** `6ac59235b8238196a0e6462de77b72413c829372`
- **Branch:** `agent/s-20261102-bedfc382/optimization-001`
- **Research area:** potential-based reward shaping for MaskablePPO; isolated files, no changes to shared train.yml.
- **Open PR conflict scan:** #6 baseline strategy, #7 evaluation, #8 infrastructure, #9 learning checkpoint/canary. Avoided their modified files.
- **Inherited verified knowledge:** main repository declares 4017 floats, 447 card indexes, 245 masked actions; no reviewed performance-specific knowledge entries at session start. PRs #6–#9 are unmerged leads only.
- **Hypothesis:** Potential-based dense feedback derived from public health (feature 5), tavern tier (10), and board size (33) improves early PPO mean placement relative to sparse terminal reward alone after 256 steps.
- **Potential:** Phi = 0.2*clip(health/40) + 0.4*clip(tier/6) + 0.4*clip(board/7), taken from normalized observe2 public globals. Shaped reward = original reward + 0.5*(0.99*Phi(next)-Phi(current)); Phi(terminal)=0.
- **Controlled design:** same PPO architecture and hyperparameters as main, same seed 22042, 256 environment steps in each arm; shaped-alpha 0 vs 0.5. Three paired full-game held-out seeds 31011–31013, one owned seat and seven TavernGym scripted seats each game.
- **Version:** TavernGym 1.1.0, engine hash `6d8712c93022ba11`; upstream pinned `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- **Run:** `python -m tavern_ai.reward_experiment --steps 256 --train-seed 22042 --out outputs/reward` on an isolated 80-minute GitHub runner. Its own push-triggered workflow saves `experiments/s-20261102-bedfc382/001-<seed>.json` and `research/sessions/s-20261102-bedfc382/metrics-001.json` ONLY after all real games and validation succeed.
- **Training status:** pending workflow; results, actual steps, game ranks, runtime, checkpoint SHA256 and CI conclusions are NOT confirmed yet.
- **Audit criteria:** completed match, engine hash, all eight placements, legal action checks, protective truncations zero. Mean rank, top4, winner rate and paired-seed ranks are descriptive; N=3 is underpowered and may not show a gain.
- **Checkpoint durability:** session-specific `outputs/reward/{control,shaped}.zip` uploaded as expiring Actions artifacts (30 days), NOT permanently persisted. Metadata JSON includes SHA256.
- **Pending evidence:** expected from session workflow (not the shared CI); no fabricated receipts or performance claims.
- **Reusable idea:** potential shaping with terminal-zero potential preserves discounted returns up to the episode's initial-state constant, assuming matching gamma and full episodes; must still test finite PPO performance.
- **Next round:** inspect actual logs, diagnose failures, compare larger evaluation seeds; only consider larger steps if experiment is stable.


## Initial real run failure and correction
- First session run [41413209781](https://github.com/sstxww/reinforcement-learning/actions/runs/41413209781) verified simulator `1.1.0 / 6d8712c93022ba11 / 4017×447×245`, passed reward unit tests, and trained both 256-step PPO arms sufficiently to save both checkpoints; **the first unguarded model evaluation did not complete**.
- Failure: original `canary.run(model)` allowed untrained deterministic model to repeat optional actions indefinitely, raising `RuntimeError: Full-game safety limit exceeded` in `canary.py:54` after its 30,000-cycle safety limit. No successful receipt was produced from this run.
- Fix within session-owned file: evaluate both arms using a dedicated genuine `Game` driver with identical deterministic 48-actions-per-turn cap; prefer legal end-turn action 0, fall back to official baseline for mandatory choices; validate action mask before each step. Record forced fallback count, zero/actual illegal actions and eight placements in real receipts.
- Initial run model artifact `s-20261102-bedfc382-models-41413209781` is temporary (30 days); rerun re-trains both arms to preserve standalone reproducibility.
- This is an engineering stability repair, **not evidence that reward shaping improves placements**.
