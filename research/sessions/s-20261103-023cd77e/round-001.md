# V7 round 001 — verified raw PPO rank-eight recurrence on new held-out seed

**Session:** `s-20261103-023cd77e` | **Base main:** `3a745c6f6a48c65528bcbeb81b8627b8db93f046` | **New code:** `tavern_ai/paired_buy_gate_023cd77e.py` + `tests/test_paired_buy_gate_023cd77e.py` + isolated read-only workflow.

## Actual run and identities
- Genuine [Actions #41512162363](https://github.com/sstxww/reinforcement-learning/actions/runs/41512162363), completed/success, source HEAD `e60af17ac50e68300b2d08304c6f0199370ca005`.
- Engine verified pinned TavernGym 1.1.0, source `6d8712c93022ba11`, observe2 4017 floats/447 card slots/245 legal masked actions.
- Registered 1408-step unpromoted Release model restored and SHA256 verified `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; tokenless CPU load verified. **0 new training steps.** Source original optimzier archive structurally preflighted; no fresh PPO optimizer continuation claimed.
- Original per-game complete JSONs / trace-first32 / gate report downloaded in [Artifact #13175145044](https://github.com/sstxww/reinforcement-learning/actions/runs/41512162363/artifacts/13175145044), archive digest `331af5aece180a071ef96f8063cce0cdd344d2961383cbbd6bef081caa86c0ca`, expires 2026-11-16 19:44:05 UTC. Originals SHA256 baseline `9879a81449cd93a93656d9095ed3651f7a95df2e9f0713d53c440e9429f59e73`, raw model `85c8ed45dc9e80ac3c9dd24a88440382ca390bff849f5582e33773754b087787`, paired report `46004fe134401d25aad4d6ddc92a242874302eb8b37ff5473c4904724c68d9df`.
- **Archived projection warning:** `experiments/s-20261103-023cd77e/*.json` reproduces all top-level game identity, placement and action-summary fields directly from the original verified receipt, but omits `trace_first_32`; its `evidence_projection.original_receipt_sha256` binds the original, which must be downloaded before artifact expiry if full trace is required.

## Same seed 99711, seat0, seven scripted bots

| Metric | Real baseline | Raw 1408-step PPO |
|---|---:|---:|
| Completed unassisted eight-player match | yes | yes |
| Controlled seat final rank | 7 | 8 |
| Decisions | 38 | 119 |
| BUY chosen / mask-legal exposures | 13 / 20 | 0 / 35 |
| FREEZE | 0 | 70 |
| REROLL | 0 | 39 |
| Turn/combat truncated | no | no |

The ranks are **not confidence intervals** (n=1). Buying 0 across 35 BUY-mask-legal decision exposures is a model behavior observation, **not** proof every state allowed an affordable or beneficial purchase, nor proof a changed reward/lr would fix behavior. Controlled model used no guard/rescue. The original engine's raw action2 is now correctly attributed FREEZE, not ambiguous OTHER.

## Tests / CI / corrective action
- New fail-closed comparator rejects wrong registered SHA, seed/engine mismatch, assisted counters, fake placement, impossible buy opportunities, misreported percentages and non-permutation eight-seat ranks.
- [Initial PR CI #41512327500](https://github.com/sstxww/reinforcement-learning/actions/runs/41512327500) had **395 tests passed, one skipped**, but PR evidence gate failed with "Missing independent agent game receipt", because run had not finished when Draft PR created. The defect was missing true receipt, *not a red unit test*. Recovered original Artifact and committed truthful game projections. Re-run must be checked on exact new head.
- No new Release and no Best/Champion promotion. No formal TavernArena. This result is **research evidence**, not a successful policy enhancement.
- The present branch is **not integrated**. No exclusive main merge lock acquired; only reviewer/integrator may merge after latest-head checks.

## Next controlled hypothesis
Separate raw action decoding from actual economic affordability and post-action state transitions; log publicly visible gold and shop/board before and after BUY-legal decisions. Compare candidate and baseline at matched seed/seat; do not retrain blindly from the same rank8 candidate.
