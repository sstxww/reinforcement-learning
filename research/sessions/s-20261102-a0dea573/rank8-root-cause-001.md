# Rank-eight root-cause evidence synthesis (V5 R001)

This is an analysis of **previously recorded authentic TavernGym games**, not new games played in this session. Source files and immutable model digests are identified below. No causal claim is promoted from action correlation alone.

## Three independent evidence groups

1. **1280-step V2, pure model**, seed `945077`, original source `reports/s-20261102-9450775f/model-gate.json`: `completed=true`, `agent_placement=8`, 122 actions, **41 REFRESH (raw ID 1)**, **70 FREEZE (raw ID 2)**, zero BUY (IDs 8–15), 37 decision states with masked BUY available; `forced_end_turns=0`, `baseline_fallback_actions=0`. The same file reports `same_observation_action_repeat_count=0`, so identical states/action loops were *not* proven by this probe.

2. **1280-step V2, two pure model games**, seeds `45111,45112`, source `reports/s-20261102-83d91476/001-buy-opportunity-report.json` with original Actions run `41428098018`: candidate ranks `[8,8]`, 74 BUY-legal decision exposures and **0 BUY**, 222/248 actions with raw IDs 1 or 2, **0 forced END**; baseline same seeds `[6,7]`, 33 BUY / 48 BUY-legal exposures. These are correlated per-decision exposures, not 74 independent shopping windows.

3. **1408-step V5, pure model**, seed `99128`, source `reports/s-20261102-68099929/003-buy-opportunity.json`: completed model and baseline both rank 8; candidate 117 decisions, 35 BUY-legal exposures, **0 BUY**, 37 rerolls and 0 guard-forced ends; baseline 39 decisions, **14 BUY** across 21 BUY-legal exposures. Weight SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` from `models/registry.json`.

4. **1280-step V2, unassisted raw diagnostic that did NOT finish**, seed `87102`, source `reports/s-20261102-ba09e2d4/002-action-opportunities.json`: 6,000 bounded model-controlled decisions but no complete eight-seat game. At turn 3 the policy executed **2,978 HERO_POWER** and **2,977 CANCEL** actions; zero BUY across 10 BUY-legal decision exposures. Ended at turn 3 due to diagnostic iteration cap, so **NO placement, no completed-game receipt**. This is direct evidence of a severe action-family oscillation for this checkpoint/seed, while not yet proving why weights favor the oscillation.

## Findings vs hypotheses

**Established observations**
- At least V2 and 1408-step V5 checkpoints repeatedly fail to choose BUY despite legal opportunities, often rank 8. An additional incomplete V2 diagnostic demonstrated a HERO_POWER↔CANCEL oscillation and failure to progress on one seed.
- The original V2 pure model strongly favors REFRESH and FREEZE in the above matched game.
- Increasing reported PPO total steps from 1280 to 1408 has not demonstrated better held-out placements (V5 `[8,8,8]` on seeds 99125–99127, source canonical `models/registry.json`).
- Some guarded model games rely on forced END; these cannot be combined with model-only performance.

**Not established**
- Legal BUY does **not** prove affordable/desirable purchase; observations do not include a counterfactual evaluator.
- Repeated action IDs do **not** prove the TavernGym state was unchanged or a deterministic no-op.
- Whether reward design, feature scaling, card IDs, action logits, end-turn mask, PPO optimization, or dataset/distribution shift is the causal root has not been isolated.
- No valid model strength promotion, fairness-adjusted rank improvement, or stronger self-play model has been shown.

## Falsifiable next experiments before more PPO steps

1. On one unmodified checkpoint and matched baseline, log gold before/after, public shop/board state changes, legal action counts, raw logits and chosen action families at the first ten BUY-legal decision states. Keep strictly public observations and bounded logs.
2. Reproduce at least three held-out seeds with controlled seat rotations and record pure-model versus guarded policies separately.
3. Perturb only the action-family logits or a *bounded* legal purchase opportunity rule in an isolated diagnostic arm (no Champion overwrite); compare economic behavior, game completion, guard actions and rank to unchanged original.
4. If behavior improves, test a small masked behavior-cloning teacher pilot and short **verified-resume** PPO continuation, using the same independent seeds; no mass training until durable release SHA/load/resume are confirmed.
5. A correction must beat the original on **held-out full games**, not merely increase BUY count; log confidence interval and model hash.

## This session execution
Training steps: **0**. Own new true-game evidence: **pending isolated Actions #41450329264**. No changes to existing model files or global evaluation configuration. No formal ranked Arena activity.
