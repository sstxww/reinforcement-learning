# Session s-20261102-c0039389 — STATUS

- **Status:** experiment source and regression gates authored; full-game Actions evidence pending.
- **Branch:** `agent/s-20261102-c0039389/optimization-001`.
- **Main baseline:** `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **Hypothesis:** existing seat-0-only evaluation can conceal controlled-seat sensitivity; examine seat 0 versus seat 4 with exactly the same original BaselinePolicy and independent paired seeds.
- **Scope:** only new `tavern_ai/seat_position_experiment.py`, `tests/test_seat_position_experiment.py`, this session's workflow, receipts/reports, session logs and knowledge proposal. Do not edit shared modules or another session.
- **Engine:** pinned TavernGym 1.1.0, source fingerprint `6d8712c93022ba11`, observe2 [4017 float, 447 card, 245 actions]; must be verified at real runner startup.
- **Research mode:** controlled-seat evaluation **engineering** study, not PPO training. Gradient steps: 0. Candidate policy: unchanged original baseline, not PPO.
- **Planned own canary:** controlled seat 4, seed 45600; required receipt `experiments/s-20261102-c0039389/001-45600.json`.
- **Planned held-out pairs:** seeds 45601, 45602, 45603, seat 0 and seat 4; only genuine Game.is_over() results qualify.
- **Training/checkpoint:** no new weights, no model checkpoint; no Best/Latest promotion. Existing best model is not established by this experiment.
- **Actions:** pending isolated branch-triggered run. Artifacts retention 30 days; the JSON evidence is committed separately when successful.
- **PR:** create after a successful own candidate game and evidence commit. CI must pass on latest PR head; merging reserved to integrator.
- **Known blockers:** none proven in this experiment yet. If workflow fails, inspect the real failed job and record root cause and repair.
- **Next hypothesis:** if seat-dependent ranks diverge, independently quantify across more seed/seat combinations before any model comparison. No causal claims from three pairs.
