# Rank-eight problem: evidence-based triage (2026-11-02)

Session s-20261102-4ba6d58f; baseline main at start 3c65ffd0380d6269e6b39c7bf1ca2d84281546d8. This report is a **code-and-other-sessions-evidence audit**, NOT a new model-controlled behavior experiment and NOT a definitive causal explanation.

## Confirmed in versioned evidence
- [PR #15](https://github.com/sstxww/reinforcement-learning/pull/15) states genuine V1→V2 MaskablePPO resume from 256 to 1,280 total steps; on four heldout seeds both V1 and V2 placed [8,8,8,8]. The paired scripted baseline placed [7,6,8,8]. Zero observed new-model improvement, small n; no Champion.
- [PR #60](https://github.com/sstxww/reinforcement-learning/pull/60) describes **three** genuine eight-seat low-learning-rate PPO games: all rank 8, 21 chosen END_TURN in 36 model actions, **zero BUY**, and **zero safety forced END_TURN**. Its reference model did 20 BUY in 875 actions across three games (placements [8,8,7]), with 21 forced ends and max run of 40 identical actions. These are different failure phenotypes; sample sizes 3 each, and the PR is draft/dependent.
- In shared `tavern_ai/canary.py`, the model chooses deterministic `model.predict(... action_masks=mask)` with legal-mask validation, but the receipt saves only total decision count, not per-action or per-turn legal opportunity counters. It cannot currently tell whether BUY was legal when END_TURN was chosen, or quantify spent gold, tavern upgrades and no-progress repetitions.
- In shared `tavern_ai/train.py`, model continuation uses `MaskablePPO.load` and `reset_num_timesteps=False`. It has no prior independent file digest check and no separate optimizer-continuation integrity test in main.
- One independent **rule baseline** full-game canary in this session (seed 49123) placed third. This demonstrates an authentic complete engineering game only; it cannot prove baseline general strength and is not a PPO benchmark.

## Competing falsifiable root-cause hypotheses
1. **Premature voluntary END_TURN** in the low-LR checkpoint: strong descriptive action-frequency evidence, BUT no legal-BUY-opportunity denominator. Need action masks and resources recorded before choosing END_TURN, with random seed/seat conditioning.
2. **Low-progress action loops** in another PPO checkpoint: observed repeated actions and forced turn endings, but whether same action was executed on an unchanged state versus a productive repeated action remains unknown. Record pre/post state signatures, legal actions, no-op and intervention reason.
3. **Training reward/observation-action disconnect**: plausible but unproven. Audit actual advantage/reward/loss logs, MaskablePPO action family map and online-vs-canary observation parity before changing reward.
4. **Weak scripted baseline/confounding**: baseline can often lose to seven official bots, so a universal eighth-place signal cannot be attributed solely to PPO. Compare matched seeds and controlled seat, opponent set, hero/shop randomness and sample uncertainty.

## Safe next test (NOT executed in this round)
At every model decision record seat, turn, gold, tavern tier, public board count, legal action-family counts, chosen action-family, pre/post visible state fingerprint, fallback marker and termination guard. Produce per-turn BUY-legal and BUY-chosen denominators; compare raw model to separately labelled rescued model, baseline, old PPO and candidate with held-out seeds and multiple seats. Only then choose a single fix. No large training until a Release checkpoint has independent byte hash, environment check, SB3 load and actual optimizer continuation verified.

## Outcome
A **model action pathology is documented** in other sessions, but it is **not yet established why opportunities were missed** or whether this is the cause of most eighth-place games. Current model ranking improvement: unproven. New PPO steps in this session: zero.
