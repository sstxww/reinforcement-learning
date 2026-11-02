# s-20261102-ba09e2d4 R002: targeted Hero Power ↔ Cancel guard
Base main: `e181d057e1813bec95ab5465dbdf89a5388dda5e`. Branch: `agent/s-20261102-ba09e2d4/optimization-002`. No main/upstream writes or other-session files.
Prior authentic R001 model failure: [Actions 41429473049](https://github.com/sstxww/reinforcement-learning/actions/runs/41429473049). Actual V2 Release 1,280-step PPO was independently SHA256 verified, but no real game completed by 6,000 actions. Turn 3 took 5,970 decisions; hero_power 2,978, cancel 2,977. BUY legal at ten decisions over three turns, zero actual buys. No model rank is defined for an incomplete game. Original baseline on same seed 87102 finished rank 5 (55 decisions).
Hypothesis: model is stuck in a repeated pair of hero-power/open and cancel actions. Test only one variable: an explicitly labelled opt-in guard choosing END_TURN after two pairs **if END_TURN is mask-legal**; no otherwise-illegal override, no hidden information.
Workflow: verify existing immutable V2 Release against main's canonical registry (#87) before genuine guarded full eight-seat games 87102 and 87103; one original baseline on heldout seed. Guard intervention count is saved. If either model game incomplete, preserve telemetry and leave job red. No automatic Champion or strength claim.
PPO steps trained in R002: **0**, new weights saved: **none**. R002 aims to recover ability to complete full games before attempting incremental training. Latest model run outcomes pending Actions.


## Independently verified real results — Actions 41430849292
- [Successful run](https://github.com/sstxww/reinforcement-learning/actions/runs/41430849292): canonical V2 Release SHA and metadata verified, TavernGym 1.1.0, all tests passed, two genuine guarded model-controlled full eight-player games completed; no truncations.
- Seed 87102 (prior unguarded noncompletion): guarded model rank **8**, 15 turns, 238 decisions, 4 explicit legal-END_TURN guard interventions; same-seed Baseline rank **5**. Real model receipt experiments/s-20261102-ba09e2d4/003-87102-guarded.json.
- Seed 87103 (heldout): guarded model rank **8**, 16 turns, 105 decisions, 0 guard interventions; original Baseline rank **7**. Real model receipt experiments/s-20261102-ba09e2d4/004-87103-guarded.json.
- BUY actions: **0 in both games**, while BUY was legal on **7 and 6 distinct turns** (35 and 33 decision points). Legal opportunity does not establish that purchase was always optimal.
- Descriptive mean rank 8.0 guarded versus 6.0 Baseline; paired differences +3/+1, n=2 too small for any promotion claim. Guard solved one full-game engineering failure, NOT strength.
- IMPORTANT telemetry wording: model_end_turns is an executed END_TURN count including explicitly guarded ones. In seed 87102: 7 executed, 4 guarded, 3 unmodified-model proposed. In seed 87103: 6 executed, 0 guarded.
- No R002 PPO training steps; no new weights or Champion. Next P3 hypothesis: public-observation economical action selection/buy starvation; verify before any large-scale training.
