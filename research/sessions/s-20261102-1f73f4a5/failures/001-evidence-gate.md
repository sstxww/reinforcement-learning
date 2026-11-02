# Failure 001 — draft PR CI started before genuine receipt commit

- Failure signature: `Missing independent agent game receipt` in `scripts/check_pr_evidence.py`.
- Initial PR gate: https://github.com/sstxww/reinforcement-learning/actions/runs/41420340906
- Failure step: `Unit tests and PR evidence`; pytest `21 passed` before receipt check.
- Reproduction cause: PR #61 created as Draft at code head `d3a1df791e35169bb986f77a4e66da8445c1b391`, while actual experiment was still training. At that commit, `experiments/s-20261102-1f73f4a5/` intentionally had no fabricated JSON receipts.
- Fix: real dedicated job https://github.com/sstxww/reinforcement-learning/actions/runs/41420063194 completed 6 eight-seat matches, validated all four heldout receipts, and committed actual JSON evidence on the session's own branch (commit `5e0f94d67f10841c0ba6f9d561d68eeb136c06d5`).
- After-fix verification: the actual experiment and receipt validations succeeded. Public CI on newest PR head **PENDING recheck at time of this report**, must not claim final CI passed until confirmed.
- No dummy match or unrelated retry; this is a submission-order problem, not broken Game API.
