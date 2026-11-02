# V5 P2 — rank-8 evidence synthesis and falsifiable follow-up
**Session**: `s-20261102-5ac817e2` · **Evidence status**: independent review of published reports and real GitHub Actions, **not a new model-controlled match from this session**.

## Verified source chain
- [Merged #98 original opportunity report](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-94a71ba0/001-v2-opportunities.json); actual source [Actions #41428347003](https://github.com/sstxww/reinforcement-learning/actions/runs/41428347003): one authentic guarded V2-controlled match rank 8. 42 mask-legal BUY decision states, **0 selected BUY**, 185 decisions, 68 consecutive raw identical actions and 1 external forced END. Raw action ID frequencies: Move(197)=68, Freeze(2)=60, Refresh(1)=37. The other same-seed baseline bought 16, placed 3.
- [Draft #103 original opportunity report](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-90e24c7b/optimization-001/reports/s-20261102-90e24c7b/001-opportunities.json); source [Actions #41428407299 SUCCESS](https://github.com/sstxww/reinforcement-learning/actions/runs/41428407299): three real **guarded** V2 matches on seeds 89101–89103 all placed 8. Total **521 BUY-legal decision exposures, 0 actual BUY**, 1,087 decisions, 12 forced END; matched baseline ranks [6,8,8], 41 buys. Denominator is per decision, **not 521 independent economic opportunities**.
- [Draft #107 buy-override ablation report](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-90e24c7b/optimization-002/reports/s-20261102-90e24c7b/002-buy-ablation.json); actual [Actions #41429432385 SUCCESS](https://github.com/sstxww/reinforcement-learning/actions/runs/41429432385), seeds 89111–89113, 3 full matches per arm:
  - Rule baseline: **40 BUY, 0 forced END**, ranks [8,8,8], decisions 131.
  - Unmodified V2 with same END guard: **0 BUY out of 99 BUY-legal decision states, 1 forced END**, ranks [8,8,8], decisions 415.
  - Frozen V2 inference + explicit first-legal-BUY override, same guard: **46 actual BUY, 18 forced END**, ranks [8,8,8], decisions 1,425.
  - Intervention altered inference only; **0 gradient steps**, no learned gain or Champion. Guarded results are not raw-policy results, and n=3 is too small for a general competitive conclusion.

## What evidence supports, and what remains unknown
**Established for the tested V2 checkpoint**: missing mask-legal BUY is a reproducible policy behavior, not solely missing legal purchase actions. The simple deterministic BUY override changes behavior but **fails to improve these three ranks** and increases intervention/decision overhead. Independent #107 PR investigation reports repeated Play/Cancel patterns with hundreds of actions; it is a plausible second bottleneck.

**Not established**: why neural logits favor Refresh/Freeze/Move/Cancel (reward, observation scaling, embedding, entropy collapse, training distribution and action-mask semantics remain candidate mechanisms). BUY-legal does not imply strategically good purchase. Model games with forced END are **guarded model** results. We have no evidence that extra PPO steps alone fix loops or that any current V5 model is a Champion. Baseline itself also ranked eighth on all three #107 seeds, so seed difficulty matters.

## Next falsifiable experiment, without large-budget training
1. On fresh held-out seeds and rotated controlled seats, sample **raw model logits/actions and public state progress** for candidate Play/Cancel and Freeze/Refresh cycles; count unique state hashes, legal mandatory-choice options, hand and board occupancy, gold spent, and actual state changes by turn. Keep privacy of opponent hidden information.
2. Define a **single opt-in, mask-legal, non-learning loop-break intervention** only when a genuine repeated public-state/action cycle occurs; separate raw-policy and guarded/overridden results and record every override.
3. Compare original V2, intervention and baseline on the **same fresh paired seeds**. Require full 8-seat game completion, receipts, action legality, timeout/guard counts, economics and stage-based metrics. If no behavioral and placement improvement, reject the intervention.
4. Before PPO continuation, verify externally pinned Release SHA256, optimizer state, engine and metadata; do **128-step smoke** only if no outstanding P0/P1 recovery gates. Do not promote without larger confidence-supported evaluation.

## Our-session boundaries
No new V2 weights were trained here; own PPO steps **0** and own PPO-controlled games **0**. This report does not assert a fix, change official policy or enter ranked Arena. Its source evidence comes from other agents' immutable run references and committed reports.
