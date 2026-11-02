# s-20261102-1b82df52 — Round 001: paired signed-log numeric observation pilot

## Identity / scope
- Session: `s-20261102-1b82df52`; branch: `agent/s-20261102-1b82df52/optimization-001`; PR: https://github.com/sstxww/reinforcement-learning/pull/17 (draft; review-only).
- Starting `main` commit: `6ac59235b8238196a0e6462de77b72413c829372`.
- Code commits: `0d54a942f57c3d16828b73bf2bbe357db412049c` (experiment); `c9f6d5902a20c0c861b4384ba3015a59af7fdbad` (per-turn safety fix). The Action committed actual receipts in `60011dff38c47783eeebcf7c0433f87bc9c9a632`.
- Ownership: `tavern_ai/log_extractor.py`, `tavern_ai/experiment_logscale.py`, `tests/test_logscale_extractor.py`, own workflow and experiment folders. No edits to other Agents' files.
- Existing guidance reviewed: `README.md`, `AGENTS.md`, `docs/PROJECT_BACKGROUND.md`, `docs/SESSION_PROTOCOL.md`, `research/knowledge/README.md`, `research/sessions/` (main had only `.gitkeep`); open PRs #6 (strategy), #7 (evaluation), #8 (infrastructure), #9 (training), and recent successful/failed Actions. PR hypotheses were **not** regarded as merged proof.
- Paper context: AutoTavern, https://huggingface.co/papers/2610.33845 ; our opt-in transform is our own hypothesis, **not** a finding of that paper.

## Hypothesis and experimental control
Could an odd monotonic signed-log compression of large numerical inputs improve the stability or outcomes of small-budget PPO, compared with the original V1 numeric encoder?

- A (control): existing `TavernExtractor`, numeric features clipped to [-500,500] and passed to the same network.
- B (candidate): `LogTavernExtractor`, `sign(x) * log1p(abs(clamp(x,-500,500)))` before the same numeric network.
- Identical model architecture, policy settings, training seed, evaluation seeds and legal action masks. No change to shared `train.py`, `canary.py`, `baseline.py`, `evaluate.py`.
- Both arms use the same independent action-cap executor (at >=45 actions in a turn, choose action 0 if legal). This is an evaluation-time guard, not a PPO architectural improvement. It is recorded in each receipt.

## Engine / reproducibility
- TavernGym 1.1.0; upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, approved patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`; source hash `6d8712c93022ba11`.
- Pinned `observe2`: 4017 float features, 447 card slots, 245 legal-masked discrete actions, 3984 indexed cards. Both branches passed real engine verification, legal-action reset/step preflight and targeted extractor unit tests.
- `MaskablePPO` / MultiInputPolicy, CPU, deterministic evaluation, 128 rollout steps, batch 64, 2 epochs, LR 3e-4, gamma 0.99, GAE 0.95, entropy 0.01, pi/vf [128], extractor dim 256.
- PPO training seed: 71002 **for each arm**; requested and actual steps 256 + 256 = **512**. Independent evaluation seeds: 32001, 32002, 32003, with 7 simulator rule bots for each controlled seat.
- Reproduction from this branch on a Linux runner: install `.[train,test]`, `bash scripts/bootstrap_engine.sh`, then `python -m tavern_ai.experiment_logscale --session-id s-20261102-1b82df52 --steps 256 --train-seed 71002 --eval-seed-start 32001 --games 3`. Run in an isolated working directory with a fixed resource timeout. CI workflow uses an 80-minute job timeout and a 55-minute experiment timeout.
- Successful run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413617114 ; compact, source-generated metrics in `research/sessions/s-20261102-1b82df52/comparison.json`.

## One failed iteration and the correction
- First run https://github.com/sstxww/reinforcement-learning/actions/runs/41412975503 installed the engine, passed tests and began real training, but the newly initialized raw-policy model repeatedly acted without ending turns. The genuine `canary.run` terminated with `RuntimeError: Full-game safety limit exceeded`. **No successful match was claimed for this run.**
- Fixed in `c9f6d590` by adding a bounded, legal, deterministic model execution harness **only to the session-specific experiment**. Both experimental models get the identical action cap, and real `Game.is_over()` plus receipt validation are required.
- The second Action succeeded, committed generated JSON and preserved checkpoints in a session-unique artifact.

## Actual complete eight-seat game outcomes

| Seed | Raw seat 0 rank | Signed-log seat 0 rank | Candidate controlled decisions | Candidate all 8 placements |
| --- | ---: | ---: | ---: | --- |
| 32001 | 8 | 8 | 107 | [8,5,7,1,2,6,4,3] |
| 32002 | 8 | 8 | 195 | [8,4,2,1,7,5,6,3] |
| 32003 | 8 | 8 | 204 | [8,2,4,3,5,6,7,1] |

- Raw control placements: seed 32001 [8,7,4,5,2,1,6,3], seed 32002 [8,1,5,4,2,7,3,6], seed 32003 [8,2,3,7,6,5,1,4].
- Candidate turns: 16, 13, 16. Candidate forced legal end-turn actions: 2, 4, 4. Control forced end-turn actions: 2, 1, 1. These counts are part of actual receipt JSON.
- **6/6** full `Game.is_over()` matches, **zero illegal actions** (fail-closed legal-mask assertion), **zero combat truncations**, and `turn_limit_end=false` in all six verified receipts.
- The mandatory own candidate match is `experiments/s-20261102-1b82df52/001-32001.json`. Source-generated controls and matches are in the session's experiments directory.
- Mean placement: raw **8.00**, signed-log **8.00**. Top-4 rate **0/3** in each, first-place rate **0/3** in each. Paired rank deltas (signed-log minus raw) **[0,0,0]**.
- This pilot does **not** establish improved performance or compare with the V0 rule baseline as a trained-policy win criterion. The tiny training budget is a major limitation, and 3 paired games cannot establish statistical significance. All three 8th-place finishes suggest both policies are extremely weak.

## Models / custody
- GitHub Actions run `41413617114`, artifact `logscale-s-20261102-1b82df52-41413617114` (artifact ID `13126299055`, approximately 18.7 MB zipped), expires **2027-01-01**; **NOT permanently preserved**.
- Raw model `checkpoints/s-20261102-1b82df52/raw.zip`: SHA256 `d8e1453f2a9e888323c82cc59cf4fbafeac6837eb46930b4e096574140c324cb`.
- Signed-log model `checkpoints/s-20261102-1b82df52/signed_log1p.zip`: SHA256 `29854cd32e32079dd8a854aabc3a338c97095dabcbb13c701660309ef5fe8267`.
- Both checkpoint `.metadata.json` files are inside the unique run artifact. No large weights in Git; no claim of persistent recovery past expiry.
- Restore (while artifact exists): `gh run download 41413617114 --repo sstxww/reinforcement-learning --name logscale-s-20261102-1b82df52-41413617114 --dir .`, validate SHA256, then `MaskablePPO.load("checkpoints/s-20261102-1b82df52/signed_log1p.zip")` in a matching environment. The experiment script trains from scratch, rather than silently resuming a differently configured model.

## What was learned / future work
1. A naïve near-random PPO model can stall the game despite selecting legal actions. Explicit legal per-turn END_TURN caps permitted six full games in the rerun. Treat this as an executor reliability observation, **not** evidence of policy strength.
2. Feature scaling alone did not produce any observable placement gain within **256 steps/model** on three matched seeds; do not promote signed-log preprocessing into the shared training code.
3. To evaluate this hypothesis meaningfully, use 10k–100k or more steps per arm, multiple independent train seeds, more held-out games, and logged action frequencies, policy entropy, feature value histograms, sample efficiency and runtime confidence intervals.
4. Separate guard-induced early endings from intrinsic policy choices; assess how often actions are forcibly ended. Compare with V0 baseline and a learned economic action prior.
5. Persist any later worthwhile checkpoint to a durable, verified Release/object store before artifact expiry. No simulator data or temporary rollouts were committed outside the seven compact JSON files.
