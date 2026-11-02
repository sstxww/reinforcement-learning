# Session s-20261102-8cfa0c44 — STATUS

- **State:** round-001-experiment-completed, awaiting latest-head PR CI and human integration review. No competitive model gain.
- **Branch:** agent/s-20261102-8cfa0c44/optimization-001
- **PR:** https://github.com/sstxww/reinforcement-learning/pull/49 (draft).
- **Base main:** 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- **Latest documented head before this update:** a60af54ff8f307651dab494caec4ac74688dada4.
- **Hypothesis:** process-isolated real TavernGym evaluation improves full-game throughput without changing seeded results.
- **Result:** negative. Six serial games 0.042792009 s vs six two-process games 0.324538407 s (7.58x slower including spawn), even though all six seed pairs yielded identical gameplay fields. Do not merge as a claimed speed optimization.
- **Validation:** 21 targeted tests passed; 13 real eight-seat games completed. Independent seed 28700 seat-0 rank 8, 49 decisions, 13 turns, placements [8,5,7,6,1,4,3,2]; zero truncation or turn-limit ending.
- **Dedicated run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41416657474 (success).
- **Environment:** TavernGym 1.1.0, source hash 6d8712c93022ba11; 4017 floats, 447 card slots, 245 masked actions.
- **Policy:** original V0 BaselinePolicy; no model changed.
- **Actual PPO training:** 0 steps (evaluation infrastructure only); no checkpoint, optimizer state, model SHA256 or Best promotion.
- **Evidence:** experiments/s-20261102-8cfa0c44/001-*.json, reports/s-20261102-8cfa0c44/throughput-001.json, research/sessions/s-20261102-8cfa0c44/round-001.md. Shared proposal research/knowledge/proposals/s-20261102-8cfa0c44-001.md.
- **Artifacts:** GitHub Actions artifact 13127303717 expires 2026-12-02T08:58:16Z; compact evidence committed in GitHub. No model artifact.
- **Unresolved:** production CI must pass at PR's latest head. Data is an order-fixed single timing batch; performance for persistent pools/large PPO workloads remains unknown.
- **Next hypothesis:** reuse persistent process workers across multiple batches, rather than paying start cost for six short games; alternate order and use independent seeds, compare to serial. Treat as a separate round, not proven improvement.
