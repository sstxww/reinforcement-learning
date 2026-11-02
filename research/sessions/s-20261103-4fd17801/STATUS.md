# s-20261103-4fd17801 — V5 status (round 001)

- Integration: reviewed exact-head #157 code, tests and own real receipt; merged to main by another concurrent agent at `df07dd23c99079449417fa8e645cf2b6c76b9704` (not this session). No own merge.
- Branch: `agent/s-20261103-4fd17801/optimization-001`, base `df07dd23c99079449417fa8e645cf2b6c76b9704`.
- Isolated evidence workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41509213556 — was IN_PROGRESS as of first check. Final result must be checked independently.
- Source: indexed V5 1408-step experimental Release, `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` (old main registry; independent recheck pending).
- Planned gates in ACTUAL launched workflow: registered Release SHA/optimizer/engine preflight; genuine matched seed 97303 raw-model/baseline game and buy-opportunity; bounded 128-step continuation; unassisted candidate seed 97304; 14-day evidence Artifact.
- **Verified own PPO steps: 0 as of this status. Verified own completed games: 0 as of this status.** Do not count planned runs as completed; no Champion. 
- Next action: inspect exact Actions result and original evidence, isolate failures (up to two material retries), commit only authentic receipts, update this status and PR review gates.

## Verified completion after independent run

- Actions [run #41509213556](https://github.com/sstxww/reinforcement-learning/actions/runs/41509213556) is **SUCCESS** with pinned TavernGym, core regression tests, authenticated Release restore/preflight, baseline/raw source paired game, actual 128 new PPO steps, and independent raw candidate game.
- Original complete real-game receipts are now committed under `experiments/s-20261103-4fd17801/`: baseline seed97303 rank **5** (16 turns,49 decisions,18 BUY); original 1408-step raw model same seed97303 rank **8** (15 turns,106 decisions,0 BUY despite 23 masked-legal BUY decisions,24 rerolls,70 'other' old-classified actions); new 1536-step raw candidate seed97304 rank **8** (14 turns,120 decisions, no guard or truncation). No competitive improvement demonstrated; candidate-vs-old not compared on identical heldout seed.
- Parent release SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; new candidate ZIP SHA `e9eb78bb100dd2398258d7f7797b7fc589bc3ef7abd0badca34c964823a04e13`, reverified after downloading the new run's Artifact locally. New total PPO steps **1536 (added 128)**.
- Temporary [Artifact #13171409075](https://github.com/sstxww/reinforcement-learning/actions/runs/41509213556/artifacts/13171409075), expires **2026-11-16 19:26:31 UTC**; explicitly NOT durable. Index: `models/sessions/s-20261103-4fd17801/1536-candidate.json`. No new Release, no Champion.
- Targeted P2 diagnostic correctness fix: in `tavern_ai/buy_opportunity_68099929.py` classify action ID 2 as **freeze** rather than undifferentiated 'other'; regression in `tests/test_freeze_family_s_20261103_4fd17801.py`. This changes telemetry labeling only, not learned policy; exact PR CI **not yet certified**.
- Do not scale PPO: source and candidate both demonstrate rank-eight on limited genuine tests. Next step is separately measure gold/board state transitions, clarify freezing vs spend, and run seed/seat-matched post-fix candidate experiments before any promotion.
