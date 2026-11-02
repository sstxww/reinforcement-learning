# s-20261102-83d91476 R002 — confirmed negative but informative outcome

## Provenance and reproducibility
- [Actual GitHub Actions run #41429513258](https://github.com/sstxww/reinforcement-learning/actions/runs/41429513258) **SUCCESS** on head `6690f89c00de3a78b8c9a03f94a788f3276e4e4a`; [full raw 12-game Action artifact #13133189224](https://github.com/sstxww/reinforcement-learning/actions/runs/41429513258/artifacts/13133189224).
- Engine TavernGym 1.1.0 `6d8712c93022ba11` (4017 floats / 447 card IDs / 245 actions), verified at execution.
- Immutable existing V2 Release SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a` verified at runtime, no new training/model changes; 4 fresh paired seeds 45113..45116.
- 12 real complete eight-seat games: 4 raw V2 model, 4 V2-with-explicit-buy-intervention, 4 baseline. No Arena activity.
- Compact per-game receipts committed `experiments/s-20261102-83d91476/002-*.json`; full per-turn diagnostics in artifact (30-day expiry). Source/run/hash recorded in JSON report.

## Observed results
| Arm | Ranks | Mean | BUY | Legal BUY exposures | Guard-forced END_TURN |
| --- | --- | ---: | ---: | ---: | ---: |
| Raw V2 | 8, 8, 8, 8 | 8.00 | 0 | 523 | 10 |
| Explicit BUY replacement | 8, 8, 8, 8 | 8.00 | 31 | 834 | 27 |
| Baseline | 7, 8, 8, 8 | 7.75 | 54 | 105 | 0 |

All 31 overrides were native proposed **Refresh** actions (1) with mask-legal BUY; 0 replacements of Freeze (2). No rank gain on four new seeds, so a single hardcoded first-legal-BUY override is **REJECTED** as a champion policy.

**Critical purity limitation:** raw V2 required 10 guard-forced ends in 2 of its 4 games. The override arm required guard-forced ends in all 4 games (27 total). These games count as genuine full game simulations with accurately labeled intervention/guard use, **not** as pure PPO strength wins.

## Mechanistic implication
The model still ranks eighth even after genuinely purchasing 31 shop cards; mere purchase-action induction is not a complete strategy. Action loops worsen: 4 overridden games show substantial hand-play action-band use and turn-guard interventions. Distinguish whether repeated legal plays consumed/produced cards versus no meaningful board advancement before proposing fixes. More PPO steps before resolving decision progress is not justified.

## Integration state
Own R001 PR #90 merged to main at `fd5ffefe2a2067cd581edfdf620976ebb6ba684a` after green latest-HEAD PR CI. R002 [PR #105](https://github.com/sstxww/reinforcement-learning/pull/105) remains Draft. Run exact-HEAD PR CI after committing receipts; review against rapidly moving main before any merge. R002 does not claim stronger trained weights.
