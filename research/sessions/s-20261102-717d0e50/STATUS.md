# s-20261102-717d0e50 — Current status

- State: real-game and unit tests passed; PR CI pending; no candidate promotion.
- Branch: agent/s-20261102-717d0e50/optimization-001
- Main base: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Experiment source commit: 665dcaddac099fbdd2788a37bb687f5fe5e4a501
- Committed genuine receipts: c26bdd0ed8e4a9e57f34ad414ba5c76692adc780
- Verified workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41415783527 (success).
- Actual TavernGym 1.1.0 engine fingerprint: 6d8712c93022ba11. Observe2: 4017 floats, 447 cards, 245 actions.
- Ten candidate and ten control full eight-seat games on seeds 29101-29110, all completed with Game.is_over(), zero illegal actions / truncated combats / turn guard endings.
- Candidate mean rank 7.7, control mean rank 6.9 (smaller is better), mean delta candidate-control +0.8. Top4 0/10 vs 1/10; first 0/10 vs 1/10. No reliable improvement shown at n=10.
- Candidate mandatory receipt: experiments/s-20261102-717d0e50/001-29101.json (rank 8, 41 decisions, 17 turns, placements [8,1,5,7,3,2,4,6]).
- Metrics: research/sessions/s-20261102-717d0e50/metrics-001.json; all receipts in experiments/s-20261102-717d0e50/.
- Training: 0 steps (deterministic strategy), checkpoint: none, model SHA256: not applicable, Best: no promotion.
- Short-lived artifact freeze-s-20261102-717d0e50-41415783527, ID 13128190086, expires 2026-12-02 08:51:15 UTC. JSON receipts additionally persisted in this branch.
- No session-owned errors; PR CI status must be checked on latest head commit.
- Next hypothesis: use public shop value and conditional Freeze rather than unconditional end-turn Freeze.
