# AutoTavern-AI V1 · Continuous Training Lab

[中文项目背景](docs/PROJECT_BACKGROUND.md) · [并发 Agent 总控提示词](prompts/PARALLEL_AGENTS.md) · [架构](docs/ARCHITECTURE.md) · [竞技场接入](docs/ARENA.md)

An **independent** AI training/research scaffold built on the open-source [AutoTavern / TavernGym](https://github.com/MCG-NJU/AutoTavern) simulator. The goal is to build a reproducible Battlegrounds agent via a small deterministic baseline, mask-aware PPO, real eight-seat simulated games, incremental checkpoints and multiple coordinated research agents. This is **not** the official pretrained TavernAgent.

## Scope

- **Simulator:** the public TavernGym engine; downloaded as a pinned dependency, not vendored or redistributed.
- **Compatibility:** Arena observe2 / TavernGym 1.1.0, 4017 float features, 447 card indices, 245 discrete legal-masked actions.
- **V0:** deterministic baseline, mandatory full eight-player game (seat 0 vs seven scripted bots).
- **V1:** CPU-ready MaskablePPO, resuming checkpoints, evaluation, GitHub Actions weekly bounded training.
- **Multi-Agent:** parallel isolated branches and PRs, one complete eight-seat battle *per Agent* before submission; CI also plays one full match.
- **No upstream writes:** all commits and PRs go exclusively into `sstxww/reinforcement-learning`.

## Run in GitHub Actions (preferred)

Go to **Actions** in this repository. `CI · full-match gate` validates a PR and plays a genuine complete eight-seat TavernGym match. `Train · incremental V1` is designed for bounded, weekly or manually initiated GitHub-runner training. The main workflow's original 90-day Artifacts are **not** durable checkpoint storage; a proposed Release-based restoration enhancement is under review in [PR #8](https://github.com/sstxww/reinforcement-learning/pull/8). Do not assume unmerged branch workflow changes are already active on main.

## Verified V1 round-1 evidence (2026-11-02)

The original [main CI 41406564039](https://github.com/sstxww/reinforcement-learning/actions/runs/41406564039) passed 12 tests, compiled actual TavernGym 1.1.0 with `observe2` (4017 floats / 447 card IDs / 245 actions), and finished an eight-player baseline match: seed 1001, 46 decisions, seat-0 rank **7**. This is a real simulation result, not Arena Elo.

Each of four isolated research branches has committed a separate **real `Game.is_over()` receipt** (all eight placements, no truncated combats):

| Branch | Recorded full-match seed | Seat-0 decisions | Seat-0 rank | Research PR |
|---|---:|---:|---:|---|
| `agent/strategy/v1` | 11001 | 52 | 6 | [#6](https://github.com/sstxww/reinforcement-learning/pull/6) |
| `agent/learning/v1` (baseline test) | 12001 | 36 | 8 | [#9](https://github.com/sstxww/reinforcement-learning/pull/9) |
| `agent/evaluation/v1` | 13001 | 51 | 4 | [#7](https://github.com/sstxww/reinforcement-learning/pull/7) |
| `agent/infrastructure/v1` | 14001 | 41 | 7 | [#8](https://github.com/sstxww/reinforcement-learning/pull/8) |

The separate full-match CI replay succeeded on specific commits for all four roles; **future branch-head changes require their own fresh successful CI**. These research PRs remain subject to review; do not merge failed or unverified revisions.

**Actual PPO candidate:** [learning Actions 41412362662](https://github.com/sstxww/reinforcement-learning/actions/runs/41412362662) completed 256 MaskablePPO training timesteps, then a genuine model-controlled full eight-seat match (seed 1302, 149 model decisions, seat-0 rank **8**) and 3 independent seeded matches (placements **8, 8, 8**, mean rank 8, top-four 0%, first-place 0%). It is **not** a strength improvement. The prior run [41412048034](https://github.com/sstxww/reinforcement-learning/actions/runs/41412048034) also trained 256 steps but its model-controlled full game **failed** a safety bound, and must remain recorded as a failed experiment.

The successful experimental model has an actual versioned **unpromoted GitHub prerelease**: [v1-learning-9eada5801f99](https://github.com/sstxww/reinforcement-learning/releases/tag/v1-learning-9eada5801f99), with `model.zip`, `model.metadata.json`, and held-out evaluation JSON. Verified model SHA-256: `dc5195658995358e70c0d565a979b9cf05ccc5e47ae7adaa0a2f078f01cad917`. The `Best` model has **not** been established. A separate [cloud Release download → true 128-step PPO resume → full-model-game verification](https://github.com/sstxww/reinforcement-learning/actions/runs/41413508653) **succeeded**: cumulative steps 256→384, verified model SHA-256 `79f90ee56e1bf49eac86e39cb76e0df70e2316a5baf5067515bced15649829e7`, independent full-game seat0 rank 8, and 3 further rank-8 evaluation games. The resumed checkpoint is independently archived in [Release `v1-learning-resume-41413508653`](https://github.com/sstxww/reinforcement-learning/releases/tag/v1-learning-resume-41413508653) with matching published-asset digest. This verifies **technical checkpoint recovery**, not competitive improvement.

**Further parallel Learning V2:** [real Actions run 41413557445](https://github.com/sstxww/reinforcement-learning/actions/runs/41413557445) resumed the earlier 256-step release for 1,024 more true PPO steps (total **1,280**), completed a model-controlled eight-seat game (seat0 rank 8) and four fixed-seed evaluation games (ranks `[8,8,8,8]`, no improvement vs V1). The actual unpromoted [V2 model Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445) has SHA-256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. This is the newest longer trained candidate; its **own** independent Release recovery, the main scheduled training workflow, and final main-branch PR integration remain distinct validation tasks. Best is still **null**.

Fixed-seed baseline metrics are in [`reports/evaluation/v1-baseline.json`](https://github.com/sstxww/reinforcement-learning/blob/agent/evaluation/v1/reports/evaluation/v1-baseline.json): 4 games, placements `[7,6,8,8]`, mean 7.25. The strategy's single same-seed V0/V1 comparison was rank 8 vs rank 8, **no established improvement**. These results are only small descriptive samples, not TavArena rankings or significance claims.

Read [`docs/RECOVERY.md`](docs/RECOVERY.md) and [`docs/MODEL_STORAGE.md`](docs/MODEL_STORAGE.md) (proposed infrastructure PR), [`models/registry.json`](models/registry.json) and [round-1 integration tracker #2](https://github.com/sstxww/reinforcement-learning/issues/2) for model roles, outstanding gates, provenance, and safe recovery. Cache cleanup must never remove uniquely useful checkpoints, receipts or experiment reports. No official TavernArena scored match has been authorized or executed.

## Manual Linux / cloud setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[train,test]'
bash scripts/bootstrap_engine.sh
python -m pytest
python -m tavern_ai.canary --agent-id demo --seed 1001 --receipt experiments/demo/first-match.json
python -m tavern_ai.validate_receipt experiments/demo/first-match.json
python -m tavern_ai.train --steps 2048 --out checkpoints/model.zip
python -m tavern_ai.evaluate --model checkpoints/model.zip --games 3
```

For real Agent PRs, each Agent uses its own `agent/<id>/<task>` branch and commits `experiments/<id>/<run>.json` generated by a genuine full simulation.

## Training loop

1. `scripts/bootstrap_engine.sh`: downloads fixed upstream commit and checks patch checksum before installing; verifies engine fingerprint.
2. `tavern_ai/env.py`: translates the real patched single-seat Gym environment into multi-input observations for PPO.
3. `tavern_ai/model.py`: embeds the 447 card-ID slots and processes numerical observations.
4. `tavern_ai/train.py`: MaskablePPO (245 discrete actions) with resumable `model.zip` and `model.metadata.json`.
5. `tavern_ai/canary.py`: completes an **entire eight-player game** using the simulator (not a scripted fake); records final placements.
6. `tavern_ai/evaluate.py`: compares fixed held-out seeds; local bot results are **not** TavernArena Elo.

**Training-vs-arena caveat:** single-seat V1 trains against seven scripted bots, not real opponents or full independent self-play. TavernGym upstream `BatchEnv` currently uses older v1 observations; expanding scalable v2 batch training is a future improvement.

## Arena participation

See [Arena integration](docs/ARENA.md). The official client from https://rizling.top/downloads/client.py runs your local model via `tavern_ai.arena_policy:act`. This scaffold does not auto-register, enter ranked matchmaking, upload weights or print secrets. Never start ranked games without explicit owner approval.

## Rights and provenance

Our code is MIT licensed; the simulator's source is owned by its original authors. Respect [AutoTavern MIT and NOTICE](https://github.com/MCG-NJU/AutoTavern). This is an unaffiliated research project and does not ship any Blizzard client or game assets. See [NOTICE](NOTICE).