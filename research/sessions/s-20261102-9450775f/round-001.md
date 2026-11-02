# V5 round 001 — archive gate and rank-eight behavior evidence

Session: `s-20261102-9450775f`. Initial main: `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`.
Branch: `agent/s-20261102-9450775f/optimization-001`. P0 review: 68 open PRs at initial scan; another integrator concurrently merged #43 and #25. We therefore did not overwrite either PR or write main.

## Scope
Isolated non-production diagnostic `tavern_ai/model_gate_s9450775f.py` plus unit tests and bounded workflow. The tool checks SHA256, ZIP CRC, saved optimizer, metadata/engine contract, and performs **real no-fallback model inference** using public observe2 features and legal mask. A failed/incomplete model game is **not** a successful match receipt.

## Target archive
Existing GitHub Release `v2-learning-41413557445` contains `model.zip` with published asset SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a` and metadata. Publication is not equivalent to runtime load, restored optimizer, or resumed training. This audit verifies archive structure and attempts model load and bounded eight-seat gameplay. It does not yet establish full resumability by actually training.

## Evaluation design
Use fixed seed 945077; cap model decisions at 800, no baseline fallback or forced end turns. Record legal BUY opportunities vs selected BUY, END with buy legal, same-observation repeated action, per-turn action family frequencies and whether the entire match finished. No raw hidden state is exposed to policy. If incomplete, rank is null and the failure remains in a diagnostic report. A **separate unchanged baseline full game** provides this session's real engine/PR smoke-test receipt.

## Status
- New code and tests submitted to isolated branch. GitHub Actions results, candidate-game result, and full-match receipt are **pending until an actual successful run**.
- Newly trained PPO steps: **0**. Champion: **none verified**. No model promotion.
- Do not extrapolate a model's buying behavior from legal opportunities alone; a legal opportunity does not establish strategic value.
- P1 remaining: persistent model registry, real optimizer restoration test, promotion gate.
- P2 remaining: gold/board feature semantics and independent paired-seed model comparisons.
