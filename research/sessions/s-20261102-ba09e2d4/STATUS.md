# s-20261102-ba09e2d4 R002 status
- base main `e181d057e1813bec95ab5465dbdf89a5388dda5e`; branch `agent/s-20261102-ba09e2d4/optimization-002`; main canonical registry #87 reused without duplication.
- R001 historical verified baseline seed 87101 rank7, seed 87102 rank5.
- R001 historical actual raw 1,280-step PPO failed game seed 87102: hero_power 2,978 / cancel 2,977, stuck turn3, 0 buys, no rank.
- R002 tests a narrow, explicitly disclosed, mask-legal hero-cancel guard, 2 real seed-controlled model games, no forced illegal action.
- 0 new PPO steps, 0 new weights, no Champion; own unique reports/receipts only; results pending.


## Independently verified real results — Actions 41430849292
- [Successful run](https://github.com/sstxww/reinforcement-learning/actions/runs/41430849292): canonical V2 Release SHA and metadata verified, TavernGym 1.1.0, all tests passed, two genuine guarded model-controlled full eight-player games completed; no truncations.
- Seed 87102 (prior unguarded noncompletion): guarded model rank **8**, 15 turns, 238 decisions, 4 explicit legal-END_TURN guard interventions; same-seed Baseline rank **5**. Real model receipt experiments/s-20261102-ba09e2d4/003-87102-guarded.json.
- Seed 87103 (heldout): guarded model rank **8**, 16 turns, 105 decisions, 0 guard interventions; original Baseline rank **7**. Real model receipt experiments/s-20261102-ba09e2d4/004-87103-guarded.json.
- BUY actions: **0 in both games**, while BUY was legal on **7 and 6 distinct turns** (35 and 33 decision points). Legal opportunity does not establish that purchase was always optimal.
- Descriptive mean rank 8.0 guarded versus 6.0 Baseline; paired differences +3/+1, n=2 too small for any promotion claim. Guard solved one full-game engineering failure, NOT strength.
- IMPORTANT telemetry wording: model_end_turns is an executed END_TURN count including explicitly guarded ones. In seed 87102: 7 executed, 4 guarded, 3 unmodified-model proposed. In seed 87103: 6 executed, 0 guarded.
- No R002 PPO training steps; no new weights or Champion. Next P3 hypothesis: public-observation economical action selection/buy starvation; verify before any large-scale training.
