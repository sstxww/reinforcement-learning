# V5 P2 — evidence-graded diagnosis of recurring eighth place

**Session**: `s-20261103-ad1c30ff`. This is a synthesis of already committed authentic TavernGym evidence on `main`, **not** newly generated PPO matches or a causal proof. Distinct checkpoint hashes below must not be conflated.

## Verified historical model comparisons (main-owned receipts)

1. Registered Latest (experimental, unpromoted) 1408-step MaskablePPO SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`: `reports/s-20261102-68099929/002-paired-custody.json` recorded three matched raw, complete eight-player games. Model places **[8,8,8]**; scripted baseline **[6,8,8]**; descriptive paired model-minus-baseline rank difference +0.667 (higher/worse), n=3, no winner/top-four; model did not improve. Single controlled seat and tiny n prevent population claims.
2. Same registered 1408-step model seed **99128**: `reports/s-20261102-68099929/003-buy-opportunity.json` recorded **35 legal-BUY decisions and zero BUY choices** over **117 model decisions** (37 rerolls, 70 other action selections); model finished rank 8. Paired baseline had **21 legal-BUY decisions, chose BUY 14 times**, rank 8 on this same seed. Every decision counted was masked legal; temporally correlated opportunities are not independent, and a legal purchase is not automatically strategically best. But the discrepancy is a concrete policy-behavior red flag.
3. A **different** checkpoint SHA256 `ce9b73b5eea8eedccfcdd48c59105e829dbb20a4e8aa8e3dce6c7f6210a2c980` has `reports/s-20261102-880b8a71/behavior-001.json`. Its **ungarded** seed 23051 probe stopped early with `own_action_audit_budget_exhausted` on turn 7, **600** raw decisions and **502** decisions on turn 7 alone; action counts: PLAY 245, OTHER 344, END 6, UPGRADE 2, CHOOSE 3, with **28 buy-legal decisions and zero BUY**. **This raw probe is NOT a scored completed game.** Its guarded variant completed a real game at rank 8 but used one forced END; see `experiments/s-20261102-880b8a71/001-23051.json`. Guarded and unguarded performances cannot be combined into one raw-policy score.
4. Draft [#107](https://github.com/sstxww/reinforcement-learning/pull/107) tested a different V2 1280-step checkpoint with guard and an explicit masked-legal BUY override. In three matched games it increased actual buys from 0 to **46**, yet all arms remained rank **[8,8,8]**. The hybrid incurred **18 forced end-turns** versus the original guarded model's 1 and showed large PLAY/CANCEL cycles (reported 257/252, 184/175, 217/214). This is an independent **negative ablation**, not proof that BUY does not matter.

## Evidence grading and root-cause hypotheses

| Statement | Grade | Why |
| --- | --- | --- |
| Several PPO candidates do not choose BUY even when BUY is legal | **Observed** | Action-masked actual game telemetry, checkpoint and seed recorded |
| Some raw policies spend a huge number of actions on one turn / do not progress | **Observed** | 600-decision raw probe stopped on turn 7; not a completed-match result |
| Extra 128-step PPO continuation reliably improves placement | **Contradicted by tested small samples** | Registered 1408-step heldout 3/3 rank8; no demonstrated gain |
| Simply forcing masked-legal BUY fixes rank-eight | **Not supported** | #107 recorded 46 purchases but ranks remain eighth; guard reliance worsened |
| Action-mask bug or bad reward/advantage is the unique root cause | **Unproven** | Need same-state mask, policy logits and optimizer/reward tracing |
| Weak board development, PLAY/CANCEL nonprogression, poor economic choices may be joint bottlenecks | **Hypothesis supported by symptoms** | Need board/gold/hand deltas before causal attribution |

## Small, falsifiable next experiment (no bulk PPO yet)

On the **same pinned model/engine**, pre-register a fresh seed set and turn/seat protocol. For every model decision capture: gold before/after, board count and effective stats, public hand/shop, chosen action family, all legal action families, repeat action streak, public-state fingerprint change, END choice and any fallback. Separate raw-only and assisted games. Compare against deterministic baseline and a **single** intervention on resolution of PLAY/CANCEL nonprogression, **not** simultaneously changing rewards, model architecture, and all action priorities.

**Success gates**: unassisted full eight-seat completion, no illegal action, meaningful board and economic progression, fewer loops and forced ENDs, and paired placement trend with uncertainty. If no improvement, reject the change. Until a durable checkpoint and raw behavior gate pass, expanding PPO volume is not evidence-driven.

No Champion promotion, new gradient steps, model files or ranked Arena games were produced by this evidence synthesis.
