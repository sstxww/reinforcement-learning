# V5 P2 eighth-place triage — evidence-separated, not a proven causal fix

Session s-20261102-70d8074c. This is an integration synthesis of *other sessions' verifiable TavernGym 1.1.0 results*, not newly generated matches by this session. Engine SHA 6d8712c93022ba11, observe2 (4017 float / 447 card / 245 masked actions). The V2 tested model is the unpromoted 1280-step Release v2-learning-41413557445, expected SHA256 73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a.

## Independent evidence and limits
| Original source | Games | Observation | Limitation |
| --- | ---: | --- | --- |
| [PR #98](https://github.com/sstxww/reinforcement-learning/pull/98), [Actions #41428347003](https://github.com/sstxww/reinforcement-learning/actions/runs/41428347003) | one paired seed 83501; 2 complete games | Model 42 BUY-legal decision opportunities, 0 chosen BUY; proposed Move(197) 68 times, Freeze(2) 60, Refresh(1) 37; model rank 8 vs baseline 3 | Model needed one externally forced END; NOT raw model strength; n=1 |
| [PR #103](https://github.com/sstxww/reinforcement-learning/pull/103), [Actions #41428407299](https://github.com/sstxww/reinforcement-learning/actions/runs/41428407299) | 3 paired seeds 89101–89103; 6 complete games | V2: 521 BUY-legal decisions, 0 actual BUY, 12 guard-forced ENDs, ranks [8,8,8]. Baseline: 73 BUY-legal decisions, 41 actual BUY, ranks [6,8,8] | Guarded model only; 3 seeds not enough to isolate optimizer/reward cause |
| [PR #107](https://github.com/sstxww/reinforcement-learning/pull/107), [Actions #41429432385](https://github.com/sstxww/reinforcement-learning/actions/runs/41429432385) | 3 distinct new seeds 89111–89113; 9 complete games | Forced legal-BUY inference overrides yield 46 genuine buys vs 0 original, **yet all three ranks remain 8**. Forced-END guards increase from 1 (original) to 18 (hybrid). Hybrid Play/Cancel counts by game 257/252, 184/175, 217/214 | Rule intervention changes inference, not PPO weights. n=3, cannot establish general effect |

The cited PRs were Draft at review time; these are reported branch-run measurements, not integrated main policy improvements. Receipt provenance and exact-head CI must be checked again before using as formal promotion evidence.

## Narrow conclusions supported by tested states
1. **Legal-mask absence is not the sole reason for no BUY:** the measured V2 policy repeatedly passed on legal BUY opportunities.
2. **A simplistic forced-BUY rule is not sufficient:** the independent intervention produced 46 buys and no rank gain in three seeds.
3. **Nonprogression loops are a serious, observed bottleneck:** repeated Move / Freeze / Refresh and particularly Play / Cancel appear frequently. The counters alone cannot determine why these actions were legal, whether game state changed, or whether training generated this bias.
4. **Raw versus guarded policy must be labeled:** the complete-game counts above include safety-end intervention. These receipts cannot be presented as proof the PPO policy alone completes every game.
5. **Do not infer reinforcement learning is fixed by more steps:** existing V1/V2/1408 candidate comparisons show no credible rank improvement, not a validated scaling curve.

## Disprovable next diagnosis; no large PPO run yet
- On fresh heldout seeds with seat rotation, log public turn, own gold, shop price/quantity, hand occupancy, board size and own-health; legal action-mask family counts; proposed and executed action families; pre/post own-observation fingerprints; guard interventions and round transitions.
- Within each turn, detect Play/Cancel oscillations conditional on *both* actions being legal and on actual public-state changes, distinguishing mandatory/target-selection from ineffective loops. Avoid opponent hidden-state leakage.
- Run an intervention changing **only** one nonprogression rule (for example, block immediate Play→Cancel reversal when a strictly legal progress action exists), with raw-policy and guarded-policy results separated.
- Pair baseline, original PPO and intervention on disjoint seeds. Evaluate completion, illegal actions, expected opportunity use, board/hand progression, placement and uncertainty. Do not promote based on three games or one favorable seed.
- If valid action probabilities or reward/advantage logs indicate collapse, test that mechanism separately. If no observable behavior improvement, reject the intervention, preserve failure evidence and do NOT scale training.

## P1 dependency
Unified canonical Release restore is prerequisite for attributing results to the same model. Our [PR #142](https://github.com/sstxww/reinforcement-learning/pull/142) adds an isolated integrity gate; its scheduled training and game steps must be verified from Actions rather than assumed.
