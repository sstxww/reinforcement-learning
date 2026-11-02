# s-20261102-75cf9e03 — V5 P0/P1/P2 status

- **Own PR:** https://github.com/sstxww/reinforcement-learning/pull/79 ; remains Draft.
- **R001:** https://github.com/sstxww/reinforcement-learning/actions/runs/41427453982 succeeded; 87 tests; genuine baseline 8-seat seed 65810 rank 8, 33 decisions, 16 turns, clean guards. Receipt `experiments/s-20261102-75cf9e03/001-65810.json`.
- **Latest full PR CI on R002 head:** https://github.com/sstxww/reinforcement-learning/actions/runs/41428031614 succeeded including full eight-seat CI game and receipt evidence.
- **R002:** https://github.com/sstxww/reinforcement-learning/actions/runs/41428024110 FAILED on strict model-only full game safety limit (seed 65811). Actual V2 Release load and genuine PPO continuation 1280→1408 complete, new SHA256 `7eac498b502a233f7ca04b351200429f2ea8142dbec47c421f7b8f3544646a8b`. No model-only completion, no valid rank, **do not promote**.
- **Critical independent preflight defect:** schema-2 Release metadata rejected by first schema-1-only audit; shell pipe to tee masked exit. Corrected schema-2 compatibility/hash logic and fail-fast pipe in R003. See `failures/002-full-game-safety-limit.md`.
- **R003:** read-only diagnostic and persist REJECTED model from historical run Artifact, attempt true guarded 8-seat action-opportunity trace and permanent failure Release, **0 additional PPO steps**. Do not claim success until actual Actions pass.
- **Champion:** none. **Cumulative experimental model:** 1408 steps (failed strict full game; temporary Artifact until Rejected Release succeeds). No official Arena, no upstream changes.
- **Conflict handling:** PR #8 remains competing/conflicted Draft; other integrator claimed and merged PR #87 registry; do not touch shared model registry or main trainer. PR #9 remains Draft; #15 depends on it.
