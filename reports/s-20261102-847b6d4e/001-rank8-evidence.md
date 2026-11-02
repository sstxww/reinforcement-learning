# V5 rank-8 behavior evidence synthesis — evidence from existing main only

> **Scope:** This is a source-linked integration handoff, not new model training or an independent model-controlled match. No model load, new checkpoint, intervention trial, or PPO steps in this session. Keep failure attribution at the *behavior* level until action consequences and learning traces are reproduced.

## Sources and comparable denominators

| Evidence | Real game status | Legal BUY mask exposures | Actual buys | Outcome | Guard |
| --- | --- | ---: | ---: | --- | --- |
| [V2 baseline vs candidate, seeds 45111/45112](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-83d91476/001-buy-opportunity-report.json) | 2 full candidate and 2 full baseline games | 74 model | 0 model / 33 baseline | model ranks 8,8; baseline 6,7 | 0 candidate forced ends |
| [V2 seed 83501](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-94a71ba0/001-v2-opportunities.json) | one complete guarded model game | 42 | 0 | rank 8; maximum identical action 68 | 1 forced end |
| [V5 1408-step candidate seed 99128](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-68099929/003-buy-opportunity.json) | one complete model and baseline game | 35 model; 21 baseline | 0 model; 14 baseline | both rank 8 | 0 forced ends |
| [V2 raw model seed 87102](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-ba09e2d4/002-action-opportunities.json) | **INCOMPLETE**: 6000 decision cap, stopped turn 3 | 10 | 0 | rank not defined, **not a match receipt** | 0, raw model |

- V2 raw seed 87102 spent 2,978 decisions in `hero_power` and 2,977 in `cancel`; the unfinished game reveals a deterministic stall signature. [Action decoder](https://github.com/sstxww/reinforcement-learning/blob/main/tavern_ai/behavior_probe_ba09e2d4.py): IDs 4–5 hero power, 7 cancel, 8–15 BUY, 1 refresh, 2 freeze.
- [Guarded V2 paired report](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json) seeds 87102/87103, complete guarded candidate ranks [8,8] vs baseline [5,7], zero purchases in 7/6 turns with legal BUY, guard overrides 4/0. **Do not pool guarded model results with raw unguarded policy results.**
- Buy-exposure counts represent **mask-legal decisions** (temporally correlated, sometimes duplicated within a turn), NOT independent purchasing opportunities and NOT proof that every purchase would have been advantageous.
- Controlled seat, sample count and source model hash must accompany comparisons: V2 checkpoint `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, V5 1408-step `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Do not attribute differences solely to learning rate or PPO update count.

## Directly supported observations
1. Non-buy behavior **is not explained solely by the action mask preventing purchases** in the sampled legal-buy states; multiple independent model runs selected BUY zero times with legal BUY positions present.
2. One genuine raw V2 trace becomes trapped at turn 3 in repeated hero-power/cancel, failing a bounded 6000-decision completion test. Other runs use refresh/freeze repetitions; deterministic action category collapse is credible.
3. Continuation to a 1408-step experimental V5 checkpoint has not eliminated the non-buy signature in its published single paired diagnostic; a larger training budget alone is not evidence of improvement.
4. Small-sample placements are descriptive; no causal attribution or confidence of strength gain has been established.

## Specific falsifiable next experiment (not performed here)
- On strictly held-out seeds with seat rotation, load exact SHA-verified V2 and V5 Release weights with engine and optimizer metadata checks.
- For each controlled-seat decision, log turn/gold, board and hand occupancy, mask-legal action families, selected action ID, before/after **public observation** hash, card purchase legality, raw PPO logits per family (no opponent private information), guard and fallback provenance.
- Measure hero-power/cancel oscillation, freeze/refresh sequences, amount of unspent gold **per turn**, legal-buy turns (not only exposure count), purchases and actual played minions, empty-board turns, plus early/mid/late shifts.
- **One variable at a time:** compare no policy override, targeted oscillation-resolution guard, and a separate legal-BUY intervention. PR #107 reports 46 forced purchases still ranking eighth in three games, so purchasing alone is not a proved repair. Do not retroactively claim this intervention as trained model behavior.
- Only if real candidate model completes independently, passes paired seeded baseline, demonstrates behavior improvement, and the original checkpoint can safely resume, run bounded PPO smoke/optimizer roundtrip. Keep Champion/Best null absent strong paired evidence.

## Integration policy
This handoff captures confirmed symptoms and clear unknowns, not new training. Source evidence remains attributed to its original sessions. Do not duplicate others' research branches, change shared model registry roles, run ranked Arena, or start large-scale PPO based on these observations.
