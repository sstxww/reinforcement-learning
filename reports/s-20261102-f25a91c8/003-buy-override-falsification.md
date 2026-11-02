# P2/P3 counterevidence: forcibly buying does not cure eighth place

**Provenance:** existing Draft [PR #107](https://github.com/sstxww/reinforcement-learning/pull/107), dependent on Draft #103, with successful real pinned TavernGym workflow [41429432385](https://github.com/sstxww/reinforcement-learning/actions/runs/41429432385), and committed `reports/s-20261102-90e24c7b/002-buy-ablation.json` and 9 complete genuine eight-seat receipts. **This session did not run those games.**

## Three fresh matched seeds, 89111..89113

| Arm | Actual BUY total across 3 games | Forced legal EndTurn interventions | Three placements |
|---|---:|---:|---|
| Unmodified deterministic baseline | 40 | 0 | [8,8,8] |
| V2 PPO policy with safety EndTurn guard | 0 | 1 | [8,8,8] |
| V2 PPO + explicit mask-legal BUY override + same safety guard | 46 | 18 | [8,8,8] |

- One narrow inference intervention replaced V2's non-BUY proposal with first mask-legal action in IDs 8..15. **It succeeded at changing behavior** (46 actual purchases), but **did not improve placement** in any of these three games.
- It increased guard-forced turn ends from 1 to 18. This weakens the hypothesis that a simple BUY preference alone is enough to fix rank 8.
- PR #107 describes pathological Play/Cancel looping even after forced purchases (reported event counts 257/252, 184/175, 217/214), keeping hand/board progression weak. A legal purchase alone does not guarantee deployment or tactical value.
- Both PPO arms are assisted/guarded, so neither supplies a pure unassisted-model competitive claim. Three seeds are exploratory, and baseline itself was also rank 8 for those seeds.
- No evidence of strength gain, no Champion. Do not merge #107 while its own prerequisite #103 is unresolved, and do not merge overlapping candidate strategies into production.

## Updated falsifiable hypothesis and decision

Observed on several real pinned engine seeds: excessive Refresh/Freeze (IDs 1/2), zero optional BUY selection, plus later Play/Cancel loops. **Two sequential bottlenecks appear**: acquisition and board-deployment/decision-loop progression. The simple hypothesis "forced BUY alone improves placement" **failed** in #107's heldout sample.

Before any additional PPO scale-up:
1. Instrument paired state transitions before/after Buy, Play, Cancel, Refresh, Freeze: publicly visible gold, hand count, board count, valid mask and same-observation hashes.
2. Isolate a single legal, bounded *deployment/progression* policy intervention (not model weights) on new heldout seeds; explicitly count overrides and forced ends.
3. Compare genuine complete-game baseline and rescued model separately; promotion requires unbiased raw-model completed games and robust heldout advantage.
4. If no positive progression signal, study action distributions/reward/advantage/observation encoding and teacher demonstration before restarting PPO.

This record reuses another independent session's existing evidence and makes **no new training, new-game, checkpoint, or arena claims**.
