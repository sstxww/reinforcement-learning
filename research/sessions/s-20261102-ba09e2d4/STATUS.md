# s-20261102-ba09e2d4 status

- Phase: `P0 integration review → P1 structural checkpoint verification → P2 actual Release probe`
- Branch: `agent/s-20261102-ba09e2d4/optimization-001`; initial base main `f29a0a6e99161aca4163e51427f6bfabbe02f76f`.
- Own engine-backed baseline full game: Actions [41427340311](https://github.com/sstxww/reinforcement-learning/actions/runs/41427340311) completed **success**. Seed 87101, seat-0 placement 7, 15 turns, 47 decisions, 0 combat truncations, no turn-limit end. Authentic committed receipt: `experiments/s-20261102-ba09e2d4/001-87101.json`.
- Tests: the branch-only initial Action's unit-test and real-game steps both succeeded. Hermetic tests are synthetic ZIP fixtures, **not** actual model restoration.
- Model registry: no verified Champion; no model promotion.
- PPO steps trained by this session: **0**; no new checkpoint.
- Next independently run candidate: read-only V2 Release hash/load/model-controlled full-game probe and same-seed baseline. Workflow launched by second-round commit, report outcome only after finished. No new PPO training until action pathology is understood.
- Open Draft PR: #80. Must verify latest-head CI and conflicts before integration.
- No official scoring Arena access, no upstream or other-session branch writes.

## 2026-11-02 R001 real failure and repair
- Full model probe [Actions #41427938674](https://github.com/sstxww/reinforcement-learning/actions/runs/41427938674) downloaded the real V2 Release and installed the pinned engine but failed at an overly strict audit schema gate: `Unsupported checkpoint metadata schema`. No model game ran, no candidate conclusion.
- Root cause confirmed by PR #9's original model trainer: published Release metadata uses schema **2** including `checkpoint_sha256` and detailed `compatibility`. Our first synthetic tests only covered schema 1.
- Implemented one bounded correction: schema 2 accepted only with matching actual digest, pinned engine, catalog, ruleset, patch and upstream. Added negative regression tests, preserving schema 1 support for existing main model format. New workflow run must be inspected; do not declare success from code alone.
