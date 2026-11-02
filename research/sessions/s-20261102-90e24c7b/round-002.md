# V5 R002 — Single-variable legal-buy priority ablation

Session: s-20261102-90e24c7b
Branch: agent/s-20261102-90e24c7b/optimization-002
Parent: own R001 PR #103 at head 7345a0f8341cfc41ef77cac85bf015f184f04bde (not independent of R001; integrate in dependency order).

## Why

R001 Actions #41428407299 completed six authentic games and documented saved V2 1,280-step checkpoint no-Buy despite 521 masked-legal Buy decisions in 3 heldout model-controlled games; baseline selected 41 Buys in 73 legal-Buy decisions. V2 ranks [8,8,8]; 12 legal EndTurn safety guard interventions. It spent many decisions on Cancel/Play/Freeze loops. The failure is reproduced but algorithmic cause is not yet proven.

## One controlled intervention

Without changing or retraining the V2 neural model, at inference time ONLY when the original model would select a **non-Buy** action while Buy indices 8–15 are mask-legal, replace that one action with the lowest mask-legal Buy slot. This is an explicit **rule-hybrid intervention**, not a PPO parameter change. All model-policy inputs remain exact own observe2 floats/cards and public legal mask. The original model, original baseline and rule-hybrid run on fresh paired seeds 89111–89113, controlled seat 0 against seven official scripted bots. All arms use the same safety cap; difference is solely Buy override. Count interventions, purchases, legal opportunity, forced ends, outcomes and per-turn own economic diagnostics; never claim learning from this rule.

## Execution evidence requirements

Planned 9 actual full eight-seat games. Workflow must download Release V2, verify immutable SHA256 73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a and load 1280-step checkpoint. TavernGym 1.1.0 pinned engine hash 6d8712c93022ba11. Must pass unit tests, real-game completion, strict receipts and write:
- experiments/s-20261102-90e24c7b/002-{baseline,model_control,model_buy_override}-{89111,89112,89113}.json
- reports/s-20261102-90e24c7b/002-buy-ablation.json

All statements about actual results remain **PENDING** until the workflow reports success and GitHub branch contains evidence. No PPO gradient steps or model weight update is planned in this ablation, and no Champion can be promoted. If Buy selection increases but rank/board remains weak, separate next-step experiments should study PLAY execution and economic teacher warm-start before costly PPO training.
