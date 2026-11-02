# s-20261103-b642f1d8 — V5 P1 integrity status

- Scope: an isolated, fail-closed regression fix on existing canonical `tavern_ai/train.py`, rather than a second trainer or model registry.
- Branch: `agent/s-20261103-b642f1d8/optimization-001` from `c8b46a64628b2540c7b6d9f3fdc1458bfe9207c3`.
- Changed: direct resume with SHA-less legacy sidecar is now rejected before loading; existing SHA-bound restore works as before; no change to saved model bytes or algorithm.
- Tests: targeted offline synthetic tests, not a simulator or real PPO-training proof.
- One-shot real eight-seat canary workflow will be independently inspected, and any bot-created receipt validated before merge. CI status not preclaimed.
- Known P0 blockers: Draft/stacked PRs, overlapping Release and shared-train changes, concurrent main movement.
- Known P1 blocker: main `train.yml` artifact-expiry fallback to random initialization; this branch does not claim that issue fixed.
- Known P2 failure: raw PPO tends to choose REFRESH/FREEZE with no BUY in legal-BUY states, plus separate HERO_POWER/CANCEL and PLAY/CANCEL loops. Not proven solved.
- Training/weights: 0 new PPO steps, 0 new releases, 0 Champion, 0 formal Arena games. No claims of successful candidate games until original receipts exist.
