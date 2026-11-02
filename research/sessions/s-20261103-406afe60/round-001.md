# V7 R001 — same-checkpoint raw PPO action selection, authentic matched eight-seat games

**Session** `s-20261103-406afe60` • **TASK_KEY** `policy/raw-ppo-sampling-vs-argmax-99831` • **BASE_MAIN_SHA** `3a745c6f6a48c65528bcbeb81b8627b8db93f046`.

## Sync / inheritance / no-race P0 decision

Read complete V7 Gmail protocol, current `AGENTS.md`, `docs/SESSION_PROTOCOL.md`, `docs/CLOSED_LOOP.md`, `models/registry.json`, main trainer/evaluator and existing PRs. Another agent merged #166, #176 and later #165 during this session; #176's full-match main CI [#41511419671](https://github.com/sstxww/reinforcement-learning/actions/runs/41511419671) ultimately passed. PR #15 remains stacked on Draft #9. Separate Draft #175 handles checkpoint no-clobber and has its own reviewer gates. This session does not claim a global atomic task lock or exclusive integrator lease and **merged no PRs**; research files are unique and own branch is isolated.

## Reproducible hypothesis

The published unpromoted V5 1,408-step PPO's deterministic argmax selects FREEZE/REFRESH repeatedly and may avoid BUY because legal BUY probability is spread over several actions. To probe only inference selection, hold **exact model bytes** and game seed/controlled seat/official bots fixed and compare unassisted `model.predict(action_masks=mask, deterministic=True)` vs `deterministic=False`; seed torch/NumPy stochastic inference to `seed+406=100237`. **No model modification, guard, rescue or secretly switched policy**. The baseline third arm uses independent actual official baseline.

- Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617
- Model SHA256: `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`
- TavernGym 1.1.0, engine source `6d8712c93022ba11`; `observe2` 4017 floats, 447 cards, 245 legal mask actions; seat 0, seed **99831** vs seven official bots.
- Training: **new 0 steps**, inherited 1408; no new model, optimizer, Release, Best or Champion.
- Source workflow exact commit `b7260914ab2d7264cc44f1abc41f63bdf7f598f3`, [Actions #41511916662](https://github.com/sstxww/reinforcement-learning/actions/runs/41511916662), **SUCCESS**. Its tests, pinned engine, registered Release preflight, all three real matches and artifact upload passed. Evidence artifact [#13174485348](https://github.com/sstxww/reinforcement-learning/actions/runs/41511916662/artifacts/13174485348), temporary 14d; does not contain a new model.
- Follow-on independent one-shot SHA verifier/receipt importer [Actions #41512673429](https://github.com/sstxww/reinforcement-learning/actions/runs/41512673429) **SUCCESS**, committed source-byte-identical original JSON into this own branch; after import, the elevated one-shot workflow was removed to avoid indefinite privileged workflow surface. Source workflow retains read-only permissions, no scheduled loop.

## Authentic results

Each is `Game.is_over()`, `completed=true`, exactly one rank permutation, 0 forced END/fallback, 0 truncated combats, `turn_limit_end=false`; policy/model hashes and engine verified by importer.

| Source receipt (committed unchanged) | Policy | Placement | Decisions | BUY / legal BUY-decision exposures | FREEZE | REFRESH |
|---|---|---:|---:|---:|---:|---:|
| `experiments/s-20261103-406afe60/001-baseline-99831.json` | scripted baseline | 8 | 37 | 13 / 20 | 0 | 0 |
| `experiments/s-20261103-406afe60/002-argmax-99831.json` | source raw PPO argmax | 8 | 125 | 0 / 47 | 70 | 39 |
| `experiments/s-20261103-406afe60/003-sampled-99831.json` | same raw PPO stochastic | 8 | 45 | 4 / 17 | 8 | 10 |

SHA256 of original JSON bytes, independently verified before commit:
- `001-baseline-99831.json` `4149499bd7fed09b45de93b5801d1b9db4cf9dd10c58df9f3045a7944876a97b`
- `002-argmax-99831.json` `aba5a0b30e205119c0ce52e06fbc446febf8338cb24c11626410bf5f2abb61dc`
- `003-sampled-99831.json` `6355ab8757a1d6343480a2438b34f81784fb78adac7635b69efc1703592d3751`

All three rank eight. BUY rates conditional on mask-legal decision exposures are 65%, 0%, and ≈23.5%. Sampled policy still END_TURN with legal BUY on 3 occasions; action-level exposures are time-correlated and not statistically independent gold opportunities. Mean placements all 8, top4 all 0, win all 0, **n=1 per arm**; cannot calculate credible competitive improvement or Champion promotion.

## What was proven; what was not

Verified: unchanged model stochastic sampling **can** output four valid BUY actions, while deterministic argmax emitted zero in the same seed and same starting checkpoint. Freeze/reroll counts also reduced (70/39 → 8/10) but trajectories diverge under alternate choices. **No competitive rank gain**. Cannot prove stochastic sampling is generally better, that reward is the root cause, or that all remaining action family `other` IDs are inert. Prior guard-forced BUY ablation also failed to improve rank; cannot infer buying more always wins.

Engineering code `tavern_ai/raw_sampling_probe_s406afe60.py`, own synthetic tests `tests/test_raw_sampling_probe_s406afe60.py`, bounded read-only branch workflow, own validated receipts and this handoff are proposed for PR review. No own workflow failure or reruns.

## Next exact integration + research gate

Create **non-Draft** PR to main, inspect full actual patch and latest-head `CI - full-match gate` (including independent CI canary), check main drift and no privilege workflow in final diff. Main merge requires real exclusive integrator entry, required approvals and expected-head compare; if unavailable leave ready for integrator with exact SHA/CI, never force-push. Any merge needs main-head CI SUCCESS. Subsequent science: predeclare multiple new held-out seeds/seat rotations with raw deterministic vs raw sampled from exact SHA, and select one mechanism-level change only if it addresses a validated inefficiency. No additional PPO budget without better training signal.
