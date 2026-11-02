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
- **Training status:** verified: run #41413908927 completed both arms, six games and own-branch receipt commit; detailed results below.
- **Audit criteria:** completed match, engine hash, all eight placements, legal action checks, protective truncations zero. Mean rank, top4, winner rate and paired-seed ranks are descriptive; N=3 is underpowered and may not show a gain.
- **Checkpoint durability:** session-specific `outputs/reward/{control,shaped}.zip` uploaded as expiring Actions artifacts (30 days), NOT permanently persisted. Metadata JSON includes SHA256.
- **Evidence:** complete real-game receipts and metrics committed by successful private runner; no performance gains observed.
- **Reusable idea:** potential shaping with terminal-zero potential preserves discounted returns up to the episode's initial-state constant, assuming matching gamma and full episodes; must still test finite PPO performance.
- **Next round:** inspect actual logs, diagnose failures, compare larger evaluation seeds; only consider larger steps if experiment is stable.


## Initial real run failure and correction
- First session run [41413209781](https://github.com/sstxww/reinforcement-learning/actions/runs/41413209781) verified simulator `1.1.0 / 6d8712c93022ba11 / 4017×447×245`, passed reward unit tests, and trained both 256-step PPO arms sufficiently to save both checkpoints; **the first unguarded model evaluation did not complete**.
- Failure: original `canary.run(model)` allowed untrained deterministic model to repeat optional actions indefinitely, raising `RuntimeError: Full-game safety limit exceeded` in `canary.py:54` after its 30,000-cycle safety limit. No successful receipt was produced from this run.
- Fix within session-owned file: evaluate both arms using a dedicated genuine `Game` driver with identical deterministic 48-actions-per-turn cap; prefer legal end-turn action 0, fall back to official baseline for mandatory choices; validate action mask before each step. Record forced fallback count, zero/actual illegal actions and eight placements in real receipts.
- Initial run model artifact `s-20261102-bedfc382-models-41413209781` is temporary (30 days); rerun re-trains both arms to preserve standalone reproducibility.
- This is an engineering stability repair, **not evidence that reward shaping improves placements**.

## Verified experimental result (independent session workflow #41413908927)
- **Run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41413908927 — **SUCCESS**. Reward tests, fixed engine patch, both training arms, six genuine eight-player Game matches, per-match validator and own-branch evidence commit all passed.
- **Actual training:** 256 steps control (alpha 0; seed 22042) + 256 steps shaped (alpha 0.5; seed 22042) = **512 confirmed environment steps**. Each arm reached 2 terminal episodes during rollout; raw reward sum -2.0 each. Shaped bonus sum -0.529254. Gamma 0.99, PPO n_steps=128, batch=64, epochs=4, learning_rate=3e-4, entropy=0.01, CPU.
- **Engine:** TavernGym 1.1.0, source hash `6d8712c93022ba11`, observed `4017 float / 447 card / 245 action`. Engine build, source patch hash and legal-action masking all verified.
- **Independent held-out evaluation:** 3 matched random seeds **31011, 31012, 31013** on each arm. Control seat 0 ranks **[8, 8, 8]** (mean 8.00, top4 0/3, wins 0/3); shaped seat 0 ranks **[8, 8, 8]** (mean 8.00, top4 0/3, wins 0/3). Paired rank changes **[0,0,0]**. The data show NO gain at this small budget; cannot establish equivalence, superiority or infer results at longer training.
- **Personal complete eight-seat games (shaped policy with identical 48-action per-turn safety layer):**
  - `experiments/s-20261102-bedfc382/001-31011.json`: placement all 8 seats **[8,7,6,4,5,2,1,3]**; 126 controlled decisions; 18 turns; safety fallback 1.
  - `experiments/s-20261102-bedfc382/001-31012.json`: placements **[8,1,2,3,6,5,7,4]**; 224 decisions; 13 turns; safety fallback 3.
  - `experiments/s-20261102-bedfc382/001-31013.json`: placements **[8,1,5,3,7,6,4,2]**; 218 decisions; 15 turns; safety fallback 3.
- **Controls:** 3 games were also genuinely run: placements **[8,7,3,5,6,1,4,2]**, **[8,7,3,5,2,4,1,6]**, **[8,2,3,4,7,1,6,5]**. Controlled action counts [126,176,169], fallback counts [1,2,2].
- **Safety:** all 6 games reached `Game.is_over() == True`, no illegal model actions, no combat truncations, no turn-limit termination. The experiment's disclosed safety cap changed some model actions on both arms; the number of such overrides differs between arms and is a confounder when interpreting policy quality.
- **Evaluation source:** `research/sessions/s-20261102-bedfc382/metrics-001.json` and the 3 full-game JSON receipts; all pushed from successful isolated runner as own-branch commit `a0ae01cfda12d3a148bcda0368abb153f42b7412`. They were not fabricated or copied from another session's CI.
- **Control checkpoint:** SHA256 `c6d2656fd988188f24d69a8bd521dcaeaa1634dadc99671531b63d7273a7236b`.
- **Shaped checkpoint:** SHA256 `2d3d29a47063cb5aad029c0282c90e775a639634f904f19f183e6a415fc40352`.
- **Location:** session-specific Actions artifact `s-20261102-bedfc382-models-41413908927` (artifact ID `13125934555`), https://github.com/sstxww/reinforcement-learning/actions/runs/41413908927/artifacts/13125934555 ; retention expires **2026-12-02 UTC**. No verified durable checkpoint repository; not permanently archived. Recover by downloading Artifact before expiry and comparing both files to SHA256 above. Do not place zip weights into Git.
- **Outcome:** reject claim that alpha=0.5 improves placement after 256 PPO steps. This negative result and the unguarded-model-loop failure are reusable. The game driver cap is necessary for completing smoke tests with weak models, but changes evaluated behavior and should be explicitly disclosed.
- **PR:** https://github.com/sstxww/reinforcement-learning/pull/12 (draft pending CI and review); no main updates.
- **Next hypothesis:** at least 2048–8192 PPO steps per arm with separately recorded action distribution and 20+ held-out games to distinguish under-training from ineffective reward shaping; add a baseline-rule comparator and evaluate fallback frequency. Avoid cherry-picking seeds or interpreting N=3 as significant.
