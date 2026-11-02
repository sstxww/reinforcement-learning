# R001 — Distinguish PPO missed buy chances from lack of legal chances

SESSION_ID: s-20261102-94a71ba0
Base main SHA: 31dc7c82ad2fcba461706b4f324d743b5c1c2b9e
Experimental branch: agent/s-20261102-94a71ba0/optimization-001
Hypothesis: rank-eight models may choose END_TURN while at least one BUY action is legal. Previous #60 telemetry showed zero purchases for a 1e-4 candidate but did **not** establish that any purchase was legal at those decision points.

## Independent bounded test

Use genuine pinned TavernGym 1.1.0 observe2 (4017 floats, 447 card indices, 245 legal actions; source hash 6d8712c93022ba11). Download *released unpromoted V2 checkpoint*, refuse SHA mismatch, then run one true model-controlled seed 83501 and same-seed baseline. Record legal-buy decision opportunities and turns, actually selected buys, model-proposed END while BUY legal, streaks and any guard-forced END separately.

The model game uses an explicitly disclosed cap of 80 actions per turn. If any forced END occurs, its rank is **guarded model gameplay only**, never raw model strength. If game fails to finish, do not fabricate receipt. This experiment does not include new PPO training (0 steps).

## Initial condition and blockers

- #8 registry/Release integration PR is Draft and conflicted; code is not on main.
- #9 PPO training PR remains Draft and current-head check lacked success.
- #15 depends on #9 and cannot merge first.
- #51/#60 are dependent and their tiny heldout samples do not prove learning rate is causal.
- #69 observation privacy PR merged concurrently by another agent, not claimed as our merge.
- Durable V2 Release weight SHA256: 73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a.
- Latest model tracked heldout rankings [8,8,8,8], but we have not in this session independently downloaded/inferred that model before the workflow executes.

## Falsifiability

A model with BUY=0 and legal-buy opportunities=0 provides no evidence of rejecting BUY. A model with BUY=0 and positive legal-buy opportunities plus END while legal constitutes a direct behavioral observation, **not** proof that buying would have won. Actual paid gold and board growth still need follow-up state diagnostics. Small n=1 cannot demonstrate strength. Require fresh paired evaluation before any model promotion.

## CI and evidence status

Initial commit: `RUN_PENDING`. No invented match receipts, no claims of completed training or improved rank. The dedicated workflow must persist two authentic generated receipts and two JSON diagnostics to session-owned paths, and the standard PR CI must pass on final head.
