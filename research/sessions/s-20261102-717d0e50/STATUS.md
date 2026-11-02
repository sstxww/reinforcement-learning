# s-20261102-717d0e50 — Current status: Round 002

Round 001 (separate branch): PR https://github.com/sstxww/reinforcement-learning/pull/40, candidate no gain, 20 genuine games, independent PR CI passed.

Round 002 branch: agent/s-20261102-717d0e50/optimization-002, from main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
State: real three-arm 30-game experiment and unit tests passed; R002 PR independent CI needs separate verification; **no Best promotion**.
Experiment source SHA: 5610b37eec2f0fa3b2926bdc5b49b232ce9c5dac; evidence commit 2b9ff6345b956d122d2653fd8821b995d6fb199e.
Successful real workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41417682184.
Failed attempts documented in failures/002-dual-observation-layout.md; do not count them as full games.
TavernGym 1.1.0 source hash 6d8712c93022ba11; observe2 4017 float / 447 cards; 245 legal masked actions, auxiliary legacy public shop observation 3227/124.
Round 002 fresh held-out seeds 29201–29210, 10 games per arm: baseline ranks [8,6,3,6,8,7,8,8,8,6] mean 6.8 top4 10%; blind ranks [8,8,5,7,8,7,7,8,8,5] mean 7.1 top4 0%; quality ranks [8,6,7,7,8,8,7,8,8,5] mean 7.2 top4 0%. First place all arms 0%.
Candidate value gate produced 32 freezes vs 44 blind freezes. Improvement **not observed**; no significance claim with n=10.
Mandatory own candidate full match: experiments/s-20261102-717d0e50/002-29201.json, rank 8, 40 seat-0 decisions, 15 turns, placements [8,3,1,4,5,6,7,2].
Metrics: research/sessions/s-20261102-717d0e50/metrics-002.json; 30 JSON receipts saved in experiments/s-20261102-717d0e50/, all pass complete-game validation.
Training: 0 PPO steps (pure deterministic strategy). No checkpoint, Latest or Best model; no model hash.
Temporary artifact 13128082762 expires 2026-12-02 09:06:32 UTC. Git branch has permanent lightweight receipts and metrics only while branch is retained.
Next study: do not add this Freeze heuristic. Focus on strategic bottlenecks with higher expected effect; baseline is weak and early-game board development deserves further independent diagnosis; obtain more seeds before strength claims.
