# R001 — real source-model full-game evidence and public-state cycle test

## Original Actions source
- [Own original successful workflow #41513736888](https://github.com/sstxww/reinforcement-learning/actions/runs/41513736888), original commit `4dc7c03487e578cbdfc64ab80d65672ed86e3ee3`, complete successful tests / pinned engine / SHA-verified registered Release restore / genuine baseline game / raw model probe / 30-day original Artifact.
- [Artifact #13173373888](https://github.com/sstxww/reinforcement-learning/actions/runs/41513736888/artifacts/13173373888), SHA256 of downloaded ZIP `08632a7b7c8faa839ae743fc7dd06013810e55bc8549363194e64e12098c75ec`. Original baseline JSON 516 B SHA256 `31a90dc448dfec76d4517f14ef157ebdd899b10ecb68c3741eccc9f39e7a6e78`; original diagnostic JSON 1638 B SHA256 `d104ffd2533189ac37e38377ab3a8866a2f5352fbcb62f32eea9cac236ddbad6`.
- Release model `v5-s-20261102-68099929-1408-41428692617`, immutable checkpoint SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; engine TavernGym 1.1.0, fingerprint `6d8712c93022ba11`.

## Genuine eight-seat games / diagnostics
| Arm | Seed | Seat | Complete | Placement | Decisions | Model buys | Provenance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Scripted baseline | 99831 | 0 | yes | 8 | 37 | n/a | Original validated full game receipt |
| Unassisted registered 1408-step raw PPO | 99831 | 0 | yes | 8 | 125 | 0 | Original successful real-game diagnostic; **not canonical receipt** |

Raw masked BUY-legal exposures **47**; Play 2, Cancel 0, Play→Cancel 0, exact public-state-return 0. Guard/fallback 0. Baseline full ranks `[8,4,6,1,7,2,5,3]`; raw model ranks `[8,5,3,2,1,4,6,7]`. Both are full permutations of 1..8 and finished. Do not infer one seed gives a true competitive result. No source-model before/after training in this session, +0 PPO steps, +0 model Releases.

## Honest hypothesis update
The prior incomplete 1536-step rejected candidate [#181](https://github.com/sstxww/reinforcement-learning/pull/181) exhibited Play/Cancel loops; this specific 1408-step checkpoint and seed does **not**. Thus the detector had no positive mechanism events here. That is informative **negative** evidence, not proof all 1408-step runs are free of loops. Zero purchases across 47 legal-exposure decisions are directly observed; causal reason may be action preference/logits, reward, or observation model and is not isolated by this report.

## CI and integration
First PR [CI #41513809602](https://github.com/sstxww/reinforcement-learning/actions/runs/41513809602) failed the intentional real-receipt gate after **390 passed, 1 skipped**. Recovered the exact original baseline JSON from the successful Action Artifact and committed it to `experiments/s-20261103-c5d8b870/`; a new exact-HEAD PR CI must now finish. Retired the session-only push workflow in the evidence commit to avoid any seed-99831 rerun on pushes; original successful Actions URL + artifacts remain the audit trail. No independently enforced main merge lock, no direct merge, no Champion.
