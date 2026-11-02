# V5 session s-20261102-86664ac4 — current status

- Status: `completed_for_review` for P0 engineering correctness gate; **not** a PPO performance change.
- Initial main SHA: `db5e23ae8c218808821327d806b05d2604cfadfb`.
- Other agents moved main to `ef77ae6bc5d9bef09e903fac7705917ec3b7366d` during this run; no main or other session branch was written.
- Branch: `agent/s-20261102-86664ac4/optimization-001`.
- Actual isolated GitHub Actions: https://github.com/sstxww/reinforcement-learning/actions/runs/41449621980 — **success**, including pinned-engine bootstrap, Python regression tests, and a genuine complete eight-seat game.
- Authentic own match: `experiments/s-20261102-86664ac4/001-96641.json`; seed 96641, player-0 rank **4**, 14 turns, 70 player decisions, placements `[4,1,2,7,5,6,8,3]`, no truncated combat/turn-limit termination, existing strict integrity checker passes.
- PPO updates: **0**. No candidate weights produced, no Champion promotion, no Arena match.
- Code fix: route `scripts/check_pr_evidence.py` through already-shipped `validate_integrity` instead of the permissive legacy checker, with regression tests for duplicate placement, wrong version/hash, bad seed and malformed receipt.
- P1 blocker: shared `.github/workflows/train.yml` still restores only time-limited `v1-model` Actions Artifacts and quietly falls back to fresh initialization on restore failure; do not run large continuous PPO or claim guaranteed continuation.
- P2 evidence: original 1408-step candidate (model SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`) remains unpromoted; 3 independent held-out ranks `[8,8,8]`. One independent seed 99128 shows 35 legal BUY decision opportunities but 0 chosen; a different legal-BUY override study purchased 46 across 3 games without rank improvement, exposing Play/Cancel loop. Causality not established.
- Next gate: latest-main compatibility review, new PR-head CI; merge only once human/code/receipt/dependency review is finished and main CI is confirmed. Do not merge other sessions' Draft PRs blindly.
