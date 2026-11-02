# s-20261102-13020d89 R001 initial record
- Base: main 315b068bac5ab6d8403c3c9b18f8c101c0cded5d; branch agent/s-20261102-13020d89/optimization-001.
- Hypothesis: own publicly observed board size and health can improve the fixed upgrade-vs-buy schedule in main BaselinePolicy.
- Source: pinned upstream crates/taverngym/src/obs.rs (global 5 health / 40, 33 own board / 7), actions.rs (upgrade 3, buy 8..15); current observe2 compatibility tested by real CI.
- Mechanism tests: unit cases on affordability via real legal mask, health gate, choose priority, progress guard. Run via isolated Actions.
- Parameter tuning: thresholds (2,5), train seeds (73010,73011). Separate canary 73030. Independent paired seeds 73020..73023; 13 complete eight-player games if all finish. Stop after at most 55 minutes; no retry loop.
- This is a small **rule parameter search** (0 PPO steps, 0 neural gradient updates). No neural checkpoint; candidate inherits baseline's 85-action end-turn protection, tracked separately.
- Historic evidence: main baseline mean rank 7.25 from four games; open PR #60 PPO no-buy telemetry; #61/#62 BC near-bottom ranks. These are not merged conclusions.
- Live results: PENDING; do not claim success, promotion or real receipts before Actions confirms.
