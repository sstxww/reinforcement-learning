# s-20261102-2acfa761 R001 — rank-8 behavior evidence (main-backed)

## Source, identities and environmental guard

This is an **audit of genuine pre-existing real TavernGym games on main**, not newly trained results. Main uses TavernGym 1.1.0, pinned engine source hash `6d8712c93022ba11`, 4017 numeric features, 447 card slots and 245 discrete actions. All reported model weights remain unpromoted. No official scored Arena games were played.

## Independent observations

1. `reports/s-20261102-83d91476/001-buy-opportunity-report.json`: V2 Release `v2-learning-41413557445`, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, in two completed model-controlled eight-seat games ranks **[8, 8]**. A mask-legal BUY was exposed at **74** decisions and the model chose **0 BUY**. The same-seed baseline got **[6, 7]**, with **33** BUY actions across **48** legal-BUY decision exposures. V2 chose action IDs **1/2 on 222 of its 248 decisions**, and the probe records **zero guard-forced END_TURN**.
2. `tavern_ai/behavior_probe_ba09e2d4.py` on main defines the pinned action families, with action **1 = Refresh** and **2 = Freeze**. Thus this V2 policy's action allocation is dominated by refresh/freeze rather than buying; log the before/after public state and economic impact before declaring all those moves no-ops. Each repeated mask-legal opportunity is a correlated decision, NOT an independent turn or a proof that buying was the optimal choice.
3. `reports/s-20261102-68099929/003-buy-opportunity.json`: later **1,408-step** model SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, one genuine eight-seat game seed 99128; **35** decision exposures with legal BUY, **0 purchases**, 37 refresh actions and 70 other actions; baseline had **14 BUY out of 21 legal-BUY exposures**. Both controlled seats ranked **8**, with zero forced END interventions.
4. **New executed evaluation of existing genuine receipts**, workflow [41450465518](https://github.com/sstxww/reinforcement-learning/actions/runs/41450465518) SUCCESS. `tavern_ai.paired_evidence_v5` processed main's 3 matched seeds 99125–99127, exact 1,408-step model hash above. Raw model (not guard-assisted) ranks **[8,8,8]**, baseline **[6,8,8]**, mean model-minus-baseline rank difference **+0.667** (higher is worse). Descriptive game-level bootstrap 95% interval **[0,2]**; exploratory only with 3 games, no statistically reliable improvement. Committed `reports/s-20261102-2acfa761/001-actual-1408step-paired.json` to own branch.

## Confirmed narrow fault and non-confirmed causes

**Confirmed:** in these sampled decision states the model is allowed to buy according to pinned TavernGym legal masks yet persistently chooses no BUY, repeatedly using Refresh/Freeze or other actions, while the corresponding baseline buys. The symptom recurs in the 1,280- and 1,408-step candidate families. Running 128 more PPO steps in this lineage did not yield a demonstrated rank improvement.

**Not established:** exact causal root is *not* yet isolated. Candidate explanations include reward gradient bias, policy logits/action-family collapse, observation feature scaling, delayed credit assignment, invalid buy availability semantics in some specific states, or optimization/masking mismatch. No causal attribution to learning rate, masks, or network architecture from these aggregates alone.

## Next falsifiable intervention

Use an isolated, bounded experiment on the **same verified weight SHA**, with fresh heldout independent seeds: for each public-observation own-seat state, record legal BUY slot mask, spendable gold, hand/shop/board occupancy, per-action masked logits, chosen action family, and public-state deltas before and after Refresh and Freeze. Never feed hidden opponents' information into the policy.

Only after identifying the dominant legal-BUY avoidance can test **one** fixed action-family intervention (e.g., a strictly legal, state-conditioned buy-vs-refresh ablation), with raw and intervention-assisted performance reported separately. Compare matched independent seeds with Baseline and original model, real full-game completion, action counts, spend and round progression. Do **not** promote on tiny samples or start bulk PPO without validated checkpoint/optimizer restore.

## Execution boundary

This session's own PPO gradient steps: **0**; own new model-only full games: **0**; own complete **baseline** match: seed **96271**, rank **6**, 15 turns / 52 decisions, verified by [workflow 41449769964](https://github.com/sstxww/reinforcement-learning/actions/runs/41449769964). No model weights, Champion or ranked Arena activity were created by this session.
