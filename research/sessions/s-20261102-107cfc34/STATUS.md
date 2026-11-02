# Session s-20261102-107cfc34 — status

- **State:** real-engine Round 001 complete, source and genuine receipts committed; PR/CI review is pending at document creation. Do not mark model improvement or a Best promotion.
- **Unique branch:** `agent/s-20261102-107cfc34/optimization-001` from `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **Independent real run:** [Actions 41416566979](https://github.com/sstxww/reinforcement-learning/actions/runs/41416566979), success; source run SHA `d9cb67f56ac19b5226b9771553cb5025c9c7b9b5`. Unit suite 23 passed. Four full games and canonical fifth cross-check. All finished, zero illegal actions, truncated combats or turn-limit guards.
- **Actual train work:** none; training steps **0** (evaluation-engineering hypothesis). No weights, optimizer state, resumed checkpoint or persistent model saved. Do not confuse model candidate PRs with verified Best.
- **Validated measured result:** seat0 seeds 51101/51102 ranks 8,8; seat1 ranks 7,8. Mean 8.0 versus 7.5, first place 0%, top4 0% both; paired rank delta -0.5; no strength gain demonstrated. Saved report `reports/s-20261102-107cfc34/seat-paired.json`.
- **Receipts:** `experiments/s-20261102-107cfc34/001-51101.json`, `001-51101-seat1.json`, `001-51102.json`, `001-51102-seat1.json`. Receipt policy hash `41fa37e1f0567d2575cbb2320f723f96eca1915c07f7e5b4992e70f178e0f29b`.
- **Compatibility:** TavernGym 1.1.0 source hash `6d8712c93022ba11`, 4017 floats, 447 cards, 245 actions; hash/pin from `tavern_ai/contract.py`.
- **Evidence:** `research/sessions/s-20261102-107cfc34/round-001.md` and `research/knowledge/proposals/s-20261102-107cfc34-001.md`; public Actions job, unexpired 30-day job Artifact, and **permanent compact JSON in branch**. No model storage or restore claim.
- **Outstanding:** PR head CI and integration review; seat-1 result should be obtained via `controlled_placement` rather than the shared validator CLI message. Prior PPO incomplete-match and Release 403 are unresolved on main as verified historical evidence, not introduced by this branch.
- **Next plan:** review incoming verified knowledge first; independently test 4–8 held-out seeds across more seats if reasonable resource budget; avoid overlapping with other strategy PRs; no ranked Arena games.
