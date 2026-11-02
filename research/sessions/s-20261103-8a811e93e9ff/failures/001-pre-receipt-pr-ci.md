# R001 CI failure — independent game receipt not committed at PR open

- **SESSION_ID:** `s-20261103-8a811e93e9ff`
- **TASK_KEY:** `security/trusted-ci-proof-paths`
- **Failed PR CI:** https://github.com/sstxww/reinforcement-learning/actions/runs/41513875622
- **Original PR HEAD:** `399f8c10a6d23a6646538a979937c845d165cd49`
- **Job:** `125512315314`, `tests-and-full-match`, completed FAILURE.
- **Observed stdout:** `409 passed, 1 skipped in 1.10s`, then `Missing independent agent game receipt` from `scripts/check_pr_evidence.py`. Other required engine/match steps were skipped. This is an **expected real evidence gate failure**, not a Python unit-test failure.
- **Root cause (confirmed):** PR was opened before this session's own original eight-seat receipt had been downloaded/validated/committed at `experiments/s-20261103-8a811e93e9ff/001-99679.json`.
- **Repair:** the independent pinned TavernGym Actions run [41513672032](https://github.com/sstxww/reinforcement-learning/actions/runs/41513672032) completed SUCCESS, and its actual original artifact [13173858866](https://github.com/sstxww/reinforcement-learning/actions/runs/41513672032/artifacts/13173858866) contains real baseline seed 99679, seat0 rank6, placements [6,5,7,4,8,3,2,1], 16 turns, 60 decisions, no guard/truncation. Original JSON SHA256 `ca47c459578a1949885edd6104f16dfa21cd09766cd65c672a08792e93fe607f`. Byte-identical receipt committed by `8edb330eb045ebbe9c4b75011dc4cd1ba1a58fba` (blob SHA `7722f7dd770c01c705497559795207fba23a5cf9`).
- **Unverified at this write:** latest PR-head CI after receipt and source/test hardening, and any independent approval. Verify actual current HEAD, not historical failed or green SHA.
- **Attempts:** 1 known original PR CI failure for this missing-evidence issue. No fake receipt was written; no rerun of unchanged failed commit manually requested; later code/receipt commits automatically triggered fresh PR CI.
- **Training/model:** +0 PPO steps; not a PPO result, no Release or Champion change.
- **Next action:** fetch current PR #219 HEAD and corresponding latest exact-head `CI - full-match gate` run; inspect completed jobs, real CI receipt and main compatibility. Do not merge without a genuinely exclusive integrator.
