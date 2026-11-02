# Session s-20261102-509af6d2 — STATUS (2026-11-02)

- **State:** `awaiting_pr_and_final_ci`; first experimental round concluded and independently confirmed, **not promoted to Best**.
- **Owner:** this unique ChatGPT research session only; no shared branches/workflows used.
- **Branch:** `agent/s-20261102-509af6d2/optimization-001` from `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`; PR: to be opened against main after research handoff.
- **Experiment:** turn-2 Tavern upgrade deferred to turn 3, otherwise original `BaselinePolicy`; source `tavern_ai/s_20261102_509af6d2.py`; regression tests `tests/test_s_20261102_509af6d2.py`.
- **Actual training:** PPO timesteps **0** (pure rule-policy tuning). Checkpoint/optimizer/weights: **none**, thus no checkpoint to restore; `Best` model unchanged and unverified by this research.
- **Engine:** TavernGym 1.1.0, source fingerprint `6d8712c93022ba11`, observe2 4017/447/245; pinned upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`.
- **First real run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415050033 (**success**). 4 paired seeds, 8 completed matches.
- **Held-out confirmation:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415518707 (**success**). 16 new paired seeds, 32 completed matches.
- **Own candidate receipt:** `experiments/s-20261102-509af6d2/001-38101.json` (seed 38101, rank 8, 47 decisions, 16 turns, all eight ranks recorded, no truncation, `Game.is_over()` true).
- **All evidence:** `experiments/s-20261102-509af6d2/`; metrics `reports/s-20261102-509af6d2/upgrade-timing-comparison.json` and `reports/s-20261102-509af6d2/confirmation-16.json`; full report `research/sessions/s-20261102-509af6d2/round-001.md`.
- **20-seed paired result:** baseline average 7.40, first 0%, top-four 5%; candidate average 6.80, first 10%, top-four 15%. Candidate-minus-baseline mean -0.60 ranks; approximate 95% confidence interval [-1.84,+0.64] spans zero. **Improvement unconfirmed**, high variance; do not deploy or change production baseline.
- **Safety:** 40 genuine full eight-seat matches; source action mask and receipt validation; no opponent hidden-information use; no TavernArena ranked games. Own workflow paths/concurrency protect other sessions.
- **Actions artifact:** short-term backup retained 30 days per workflow configuration. JSON receipts and source live in Git branch, but are not model checkpoints.
- **Own unresolved failure:** none observed; peer PR failure signatures in research report are context only.
- **Next steps:** open PR, verify latest PR-head CI; preserve this negative/uncertain conclusion for review. A future distinct hypothesis could test state-aware upgrade timing only after observation semantics are validated.
