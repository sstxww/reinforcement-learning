# Round 001 — Real released-PPO buy-opportunity/loop diagnosis

**Session**: s-20261102-94a71ba0 • **original main base**: `31dc7c82ad2fcba461706b4f324d743b5c1c2b9e` • **PR**: https://github.com/sstxww/reinforcement-learning/pull/98

## Prior evidence / falsifiable question

Prior experiment #60: a different 1e-4 PPO model chose 21 END_TURN among only 36 decisions, purchased zero cards, and ranked 8 in 3 real games. Its evaluator did not record whether legal BUY existed when it selected other actions. That experiment cannot establish learning-rate causality. The latest durable V2 (1280 steps, a **different** model) also had four historical heldout finishes [8,8,8,8]. Test whether this actual saved V2 model also ignores *available legal* purchases on an independent seed.

## Method and version contract

Source commit `62eaf83c2d3b23220fe18f9a0a8896d5056e14ac`; pinned upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, engine 1.1.0 SHA `6d8712c93022ba11`, observe2 4017 float + 447 card index + 245 legal actions. Existing verified engine patch is installed by `scripts/bootstrap_engine.sh`; model sees only its own observe2 arrays and action_mask, not debug views or hidden opponent data.

Real GitHub Actions #41428347003: https://github.com/sstxww/reinforcement-learning/actions/runs/41428347003 completed **success**. Installs `.[train,test]`, runs full `pytest`, builds pinned TavernGym, downloads GitHub Release `v2-learning-41413557445`, checks `model.zip` SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, then runs a complete eight-seat model game and identical-seed Baseline control. Seed **83501** was fixed before running, not selected after measuring results.

The diagnostic records per-turn and aggregate counts for legal BUY masks, selected BUY, proposal END with BUY legal, exact action IDs, repeated-action streak and any forced END. For model only an explicit `--guard-cap 80` can forcibly end when the game would otherwise repeatedly act; any intervention marks this match `guarded_model_not_raw`. A full game completes only after engine `Game.is_over()`; raw turn/combat truncation invalidates receipt. No neural training, 0 PPO/BC steps, no checkpoint overwrite.

## Actual verified paired game results

| Measurement | Durable V2 model (guarded) | Rule Baseline |
| --- | ---: | ---: |
| Full genuine games | 1 | 1 |
| Seed | 83501 | 83501 |
| Seat-0 placement | **8** | **3** |
| Controlled decisions | 185 | 63 |
| Decision states with BUY legal | **42** | 34 |
| Turns with any BUY legal | 7 | 10 |
| Actual BUY actions selected | **0** | **16** |
| Model END while BUY legal | 0 | n/a |
| Externally forced END | **1** | 0 |
| Longest identical proposed-action streak | **68** | 5 |
| Complete engine, no combat truncation, no turn-limit end | yes | yes |

Model proposal IDs: `197:68` (verified Move band 196..244), `2:60` (Freeze), `1:37` (Refresh), `0:6` (EndTurn), `46:4` (Play), `3:1` (Upgrade), `16:1` (Sell), plus hero/dark gift choices. The model executed all but one proposals and received **one forced END at turn 7**; this enabled a complete genuine game but limits any raw-policy strength inference. Legal BUY counts refer to state-by-state opportunities, not distinct available cards or economically best actions.

Evidence committed by independent runner:
- `experiments/s-20261102-94a71ba0/001-83501-model.json`, placements `[8,1,7,4,2,3,5,6]`, 13 game turns, source SHA and model SHA.
- `experiments/s-20261102-94a71ba0/001-83501-baseline.json`, placements `[3,1,8,6,2,7,4,5]`, 13 game turns.
- `reports/s-20261102-94a71ba0/001-v2-opportunities.json` and `001-baseline-opportunities.json`, per-turn legal masks and intervention statistics.
- Success run https://github.com/sstxww/reinforcement-learning/actions/runs/41428347003.

## Inference and failure class

**Directly verified behavioral pathology:** this unpromoted V2 PPO entirely bypassed BUY despite 42 BUY-legal decisions and repeatedly picked available Move/Freeze/Refresh actions. This is a practical explanation for one model's weak game performance; it **does not establish RL algorithm root cause**, because action value predictions, gold/board state deltas and alternative-action counterfactuals were not measured. The prior low-LR model #60 and this V2 have different checkpoints: avoid combining counts as if one sample.

A training-throughput increase alone cannot be justified as the next solution when a saved model cannot reliably execute game economy. Reproduction/mitigation hypothesis: record whether repeated action 197 produces any public state change, then test strictly legal de-looping/Buy action behavior with fixed seed+seat-rotation on separate candidate weights; train only after release-backed resume compatibility has been verified by integration. Even if rank improves in one seed, require heldout paired samples and confidence before Champion.

## CI / integration status

Initial PR full-match CI #41428577047: **89 tests passed, 1 skipped**, then expected evidence preflight failure `Missing independent agent game receipt` because the bot had not yet committed its real game. The successful dedicated workflow added both receipts afterward. Another independent PR-head CI must run on the new evidence-bearing head; do not present the earlier failed one as passed. All changes remain in own branch; no direct main/upstream writes, no Arena, no Release/Best overwrite.
