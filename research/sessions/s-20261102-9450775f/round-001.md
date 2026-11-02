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

## Addendum: final real model-match findings after exact action-ID decoding
- Actual updated unique Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41428807486 **success**, including original engine and real no-fallback model complete eight-seat match, genuine separate baseline game and durable git evidence commit.
- Full 245-action decoder audited against PR #70 pinned Rust action families: previous 71 `other` were **70 FREEZE action ID 2 + 1 HERO_POWER action ID 4**. Not magnetize/move. `REFRESH` action ID 1 occurred 41 times; `BUY` action IDs 8..15 occurred **zero** times despite 37 legal BUY decisions. Per-turn recorded FREEZE=10 for each turn 1 through 7. Thus the proximal observed behavior is a shop-freeze/refresh loop without acquisitions, producing rank 8.
- The game completed in 122 model decisions (total TavernGym turn 16), no baseline fallback, forced END, truncation or illegal action. No best-model promotion and 0 new training steps. The 37 opportunities are legal masks, not proof that purchases were economically optimal or affordable in other contexts.
- Exact bytes, seeds and metadata in `reports/s-20261102-9450775f/model-gate.json` and `experiments/s-20261102-9450775f/001-945078.json`; V2 Release model SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- Initial evidence push was rejected due own branch concurrent documentation update and documented in failure 001; the bounded fetch+reapply repair actually passed in the latest run.
