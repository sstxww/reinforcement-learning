# Status: V5 P1 checkpoint registry — real smoke passed; PR review pending

Session: s-20261102-91b6e4a7. Main base 42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c.

Own GitHub Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41427822784
Result: SUCCESS, pinned TavernGym 1.1.0, registry offline validation/tests passed.
Own genuine eight-player full-game receipt: experiments/s-20261102-91b6e4a7/001-91031.json, committed in 65bf5ccc1a9f1dfaf7d9fef8aef7f95964cd4826.
Baseline control seat 0, seed 91031, rank 8, turns 14, decisions 51, placements [8,1,5,2,6,3,4,7], completed true, 0 truncated combats, no game turn-limit ending.

Training steps **this session = 0**. This was a baseline infrastructure smoke game, **not** a PPO model game. No new weight files, Champion or Latest. Existing V1/V2 model Release digests were indexed but not independently downloaded, loaded or resumed by this session.

Next gate: latest PR-head CI + integration review and independent Release restore with model-only full match before any production model promotion. V5 issue #78 root-cause legal BUY opportunity and no-progress traces remain unresolved; no bulk PPO train.
