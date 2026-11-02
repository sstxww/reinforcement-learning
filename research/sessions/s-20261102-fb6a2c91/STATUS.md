# AutoTavern V5 session s-20261102-fb6a2c91 — STATUS

Session owner: this independent ChatGPT conversation. Own branch: `agent/s-20261102-fb6a2c91/optimization-001`. Review: https://github.com/sstxww/reinforcement-learning/pull/133.

## Origin and P0 integration
- Main base (immutable): `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`. Main advances concurrently; do not overwrite it or another session.
- #93 held: current main has five registered candidates but #93's unit tests require exactly four and full metadata index equality; the green old-head PR CI cannot certify integration. Comment sent.
- #15 held: only Ready PR depends on #9 which is Draft and has no verified latest-head CI. No merge attempted; comment sent.
- No upstream/official ranked arena, no Champion/Best changes, no modifications to shared `train.yml`.

## Completed real evidence (this own branch)
- GitHub Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41450269678.
- Offline lineage regressions **passed**; pinned TavernGym 1.1.0 build + source hash `6d8712c93022ba11` **passed**.
- Authentic **baseline**-controlled full eight-seat game seed `92360`: completed=true, placement seat0=8, turns=14, decisions=55, `placements=[8,2,4,7,1,3,5,6]`, truncated combats=0. Exact verified and committed receipt: `experiments/s-20261102-fb6a2c91/001-92360.json`. This does not certify any PPO model.
- Existing experimental 1408-step V5 Release downloaded by independent workflow. Source tag `v5-s-20261102-68099929-1408-41428692617`; parent SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- At this STATUS update, the actual 128-step resume/child model gate is **in progress**. No child SHA/Release/true-model rank or competitive gain is asserted without later workflow evidence. Read the live job steps before updating status.

## P2 proven and falsified hypotheses
- `reports/s-20261102-83d91476/001-buy-opportunity-report.json`: V2 2 genuine games, ranks [8,8], zero buys at 74 legal BUY decision exposures, raw actions IDs 1/2 222/248; same-seed baseline ranks [6,7] with 33 buys.
- Exact pinned upstream Rust actions: 1 Refresh, 2 Freeze (toggles shop), 7 Cancel, 8..15 Buy; the action mask checks affordability (gold or health) and hand capacity.
- Draft stacked PR #107: 3 paired buy-overridden games still [8,8,8] despite 46 real buys; Play↔Cancel cycle also present. Therefore simple forced BUY is insufficient; do not promote based on action counts alone.

## Next gates
Review the genuine 128-step child SHA, 1408->1536 lineage, its model-only game (or explicit no-game failure), two-game paired evaluation when completed, published unique Release assets or a real permission blocker, and exact latest-head CI before requesting merge. An expiring Artifact is not durable model storage.
