# Round 001 — Masked PPO legal end-turn guard (real experiment)

- Session: `s-20261102-e599fa38`
- Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Experimental source commit: `0e4724e59ff0916f85fdcf2643cfa38dd22328f5`
- Branch: `agent/s-20261102-e599fa38/optimization-001`
- Workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41415158420 (**success**)
- Artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41415158420/artifacts/13128035277 (expires **2026-12-02 08:47 UTC**, not permanent)
- Integration: https://github.com/sstxww/reinforcement-learning/pull/31 (Draft; check latest head CI); never automatically merge this candidate.

## Prior evidence and selected hypothesis

Read the current main repository README, AGENTS.md, architecture, session and closed-loop rules, knowledge index and INCidents record; checked 12 open PRs and recent Actions. Existing unmerged work in PRs #12, #17, #18 used 48, 45 and 65-action guards; this session independently tests an **explicit legal end-turn cap of 32** without touching production modules. Hypothesis: the same undertrained PPO weights that loop indefinitely in an unguarded seed can finish with an auditable mask-safe cap. **This is a game-completion engineering hypothesis, not an expectation of improved placement.**

## Code changes and baseline

New isolated module: `tavern_ai/guarded_model_probe.py`; tests: `tests/test_guarded_model_probe.py`; private bounded workflow: `.github/workflows/experiment-s-20261102-e599fa38.yml`. No edits to other agents, main-only train workflow, or production canary.

Original masked PPO inference attempted a full game with the exact candidate checkpoint at seed **31071**. It failed with `RuntimeError: Full-game safety limit exceeded` after the canary's 30,000-loop guard (exit code 1); this is **not** a completed match. Original failing step and stack trace are in the successful experiment run's `Probe unguarded candidate` step.

## Genuine bounded training

- Pinned upstream commit: `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; observe2 patch SHA-256: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`
- Engine: TavernGym **1.1.0**, source hash `6d8712c93022ba11`, observe2 **4017/447/245**.
- Fresh MaskablePPO, train seed **71879**, **128 actual timesteps**, CPU, one agent against 7 scripted bots. `n_steps=128`, `batch_size=64`, `n_epochs=4`, `gamma=0.99`, `gae_lambda=0.95`, `learning_rate=3e-4`, `ent_coef=0.01`; TavernExtractor features_dim=256.
- Verification: **25/25 pytest passed**; training log reports `total_timesteps=128`; checkpoint reloaded successfully for actual game inference.
- Model SHA256: `5b66d29acccb4ecefb302f28a86d40aaa981e121fb830bfe1e752923fc602fcb`.
- Model stored only in unique short-lived Actions Artifact above, with matching `model.metadata.json`; no permanent checkpoint is claimed.

## Actual full eight-seat guarded PPO games

| Seed | Seat 0 placement | 8 seat placements | Agent decisions | Guard interventions | Complete | Combat truncation | Turn limit |
|---|---:|---|---:|---:|---|---:|---|
| 31071 | 8 | [8,6,5,1,2,4,3,7] | 141 | 2 | yes | 0 | false |
| 31072 | 8 | [8,2,7,6,4,5,3,1] | 108 | 0 | yes | 0 | false |

Both games genuinely reached `Game.is_over()` with 7 official scripted bots. The PPO is consulted for every seat-0 decision, and only **legal masked end-turn** overrides are allowed after 32 prior actions per turn. Therefore these are **guarded PPO**, not pure raw PPO, receipts.

Receipts: `experiments/s-20261102-e599fa38/001-31071.json`, `experiments/s-20261102-e599fa38/001-31072.json`. Actual logs: https://github.com/sstxww/reinforcement-learning/actions/runs/41415158420; no fabricated data.

## Held-out descriptive comparison (same seeds, n=2 per policy)

- Guarded PPO placements [8,8], mean rank **8.0**, top-4 **0/2**, first **0/2**.
- Existing deterministic baseline placements [8,6], mean rank **7.0**, top-4 **0/2**, first **0/2**.
- Paired candidate-minus-baseline differences [0,+2], mean **+1.0** (higher is worse).
- Original raw PPO fails only the recorded seed 31071; there is no complete raw-model performance record for that seed.
- Evidence supports successful termination for this controlled seed; **no strength gain**, no Best promotion, and no Arena ranking claim. Sample too small for generalization.

## Follow-up

Probe why PPO repeatedly proposes non-terminal actions; add independent action-frequency/turn diagnostics before changing architecture; use matched guard conditions for each candidate. Confirm whether reducing forced actions changes score over a larger fixed held-out seed set. Do not blindly extend small PPO training without learning evidence.
