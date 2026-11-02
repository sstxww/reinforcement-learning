# P0 open PR triage — s-20261102-83d91476 (snapshot)

Main at sampling: `c85d566cccccf5e2ef7de09b6cc95e1aa506da9c`; initial session branch base: `31dc7c82ad2fcba461706b4f324d743b5c1c2b9e`.
Open PRs besides own #90: 80, Draft 79. Counts are dynamic across concurrent sessions.

Preliminary triage buckets: A=0, B=15, C=32, D=23, E=10.

- **A:** none approved. CI, mergeability, race-free ownership, and model evidence cannot be inferred from green historical checks.
- **B:** declared dependencies or documented blockers; #8 Draft/conflicted, #9 Draft/unverified, #15 non-Draft but stacked on #9.
- **C:** requires complete review/independent evaluation; not merge-approved.
- **D:** reported negative/non-gaining studies; retain useful diagnostics, do not promote weak policies.
- **E:** overlapping topics for deduplication (mechanics catalogs, choice-index, buy-first investigations). Flagged overlap is not proof of code conflict.

|Bucket|PR|Draft|HEAD 12|Title|
|---|---|---|---|---|
|B|[#94](https://github.com/sstxww/reinforcement-learning/pull/94)|Y|`04aaa96b73ec`|[s-20261102-6b4eaf12 R001] Integrate Release checkpoint preflight + real PPO buy-opportunity diagnosis|
|B|[#93](https://github.com/sstxww/reinforcement-learning/pull/93)|Y|`41690d0d57e9`|[s-20261102-91b6e4a7 R001] V5 checkpoint Release registry, fail-closed verification & real game smoke|
|B|[#92](https://github.com/sstxww/reinforcement-learning/pull/92)|Y|`f4306604ddd1`|[s-20261102-309d57fc R001] V5 checkpoint SHA gates, model registry and bounded Release resume audit|
|B|[#88](https://github.com/sstxww/reinforcement-learning/pull/88)|Y|`fa28aad7ba5e`|[s-20261102-4ba6d58f R001] Release-backed model registry and fail-closed checkpoint verification|
|B|[#76](https://github.com/sstxww/reinforcement-learning/pull/76)|Y|`6d129de78c26`|[s-20261102-1692601b R002] Twenty new seat-rotated pairs refute robust sell-swap rank gain|
|B|[#65](https://github.com/sstxww/reinforcement-learning/pull/65)|Y|`fc772acf08e6`|[s-20261102-661adf61 R002] Official bot BC: 43 real games show transfer failure (REJECT)|
|B|[#60](https://github.com/sstxww/reinforcement-learning/pull/60)|Y|`23beccafb0cf`|[s-20261102-24728f13 R002] Real PPO telemetry: low-LR candidate never buys on heldout seeds|
|B|[#59](https://github.com/sstxww/reinforcement-learning/pull/59)|Y|`f36cd92436f7`|[s-20261102-c0039389 R002] Full eight-seat TavernGym sweep (33 complete matches; no stable seat4 gain)|
|B|[#57](https://github.com/sstxww/reinforcement-learning/pull/57)|Y|`372d5cc6cc86`|[s-20261102-64405d5e R002] 20 held-out real paired seeds confirm only a small unproven buy-first signal|
|B|[#56](https://github.com/sstxww/reinforcement-learning/pull/56)|Y|`22e1f39be1a8`|[s-20261102-8cfa0c44 R002] Persistent-vs-fresh pool: 385 real games, serial still faster|
|B|[#54](https://github.com/sstxww/reinforcement-learning/pull/54)|Y|`d0042408ea58`|[s-20261102-e599fa38 R002] Six-seed paired PPO guard-budget ablation (no strength gain)|
|B|[#53](https://github.com/sstxww/reinforcement-learning/pull/53)|Y|`fd99bd939f74`|[s-20261102-221336eb R002] Cap-3 real-game study: 40% fewer decisions but all rank 8|
|B|[#15](https://github.com/sstxww/reinforcement-learning/pull/15)|N|`ad1bf93498ab`|[V2][learning] verified 1280-step PPO resume + paired full-game benchmark (no gain)|
|B|[#9](https://github.com/sstxww/reinforcement-learning/pull/9)|Y|`5f2fa7ebb79a`|[V1][learning] resumable PPO and first-round experiment|
|B|[#8](https://github.com/sstxww/reinforcement-learning/pull/8)|Y|`97f11dc827bf`|[V1][infrastructure] first-round verified-match candidate|
|C|[#99](https://github.com/sstxww/reinforcement-learning/pull/99)|Y|`e9536ee89726`|[s-20261102-53ca82c3 R001] V5 P0: safely extract cache cleanup from conflicted PR #8|
|C|[#98](https://github.com/sstxww/reinforcement-learning/pull/98)|Y|`6c093802e0f2`|[s-20261102-94a71ba0 R001] V5 released-PPO legal BUY opportunity diagnostic (engineering)|
|C|[#97](https://github.com/sstxww/reinforcement-learning/pull/97)|Y|`cc67a6870826`|[s-20261102-7be8a4d3 R001] V5 integrate Release registry and verify bounded model recovery|
|C|[#96](https://github.com/sstxww/reinforcement-learning/pull/96)|Y|`312f93a53e95`|[s-20261102-9450775f R001] V5 SHA-verified Release model and true no-fallback rank-eight telemetry|
|C|[#95](https://github.com/sstxww/reinforcement-learning/pull/95)|Y|`f84f1230c768`|[s-20261102-decfc670 R001] Verify durable V2 model SHA/CPU inference and diagnose rank-8 buy opportunities|
|C|[#91](https://github.com/sstxww/reinforcement-learning/pull/91)|Y|`2cedb6c38693`|[s-20261102-704cec7b R001] V5 integration: durable model index, verified V2 resume, rank-8 opportunity diagnosti|
|C|[#86](https://github.com/sstxww/reinforcement-learning/pull/86)|Y|`325a20815c32`|[s-20261102-9732a21e R001] V5 gated Release-resume 128-step smoke and persistent checkpoint roundtrip|
|C|[#85](https://github.com/sstxww/reinforcement-learning/pull/85)|Y|`72eb031428c7`|[s-20261102-880b8a71 R001] V5 Release-based PPO recovery gate, 128-step smoke and rank-eight evidence|
|C|[#84](https://github.com/sstxww/reinforcement-learning/pull/84)|Y|`67edbb641037`|[V5 P1][s-20261102-902968f5] Verify durable Release hashes and bounded PPO optimizer resume|
|C|[#83](https://github.com/sstxww/reinforcement-learning/pull/83)|Y|`d3f72a002870`|[s-20261102-b45c837d R001] V5 fail-closed checkpoint registry and real-match CI gate|
|C|[#82](https://github.com/sstxww/reinforcement-learning/pull/82)|Y|`2811ed957f14`|[s-20261102-6f4c8a19 R001] Verify V2 Release SHA/optimizer, bounded PPO resume and true-game gate|
|C|[#81](https://github.com/sstxww/reinforcement-learning/pull/81)|Y|`94723a15e3ba`|[s-20261102-cacfdbae R001] V5 release-inventory audit and historical PPO resume gate|
|C|[#80](https://github.com/sstxww/reinforcement-learning/pull/80)|Y|`4e62c69f6d04`|[s-20261102-ba09e2d4 R001] V5 unpromoted model registry and SHA256 checkpoint audit|
|C|[#79](https://github.com/sstxww/reinforcement-learning/pull/79)|Y|`369eb880465e`|[s-20261102-75cf9e03 R001] V5 integration: fail-closed persisted PPO checkpoint preflight|
|C|[#73](https://github.com/sstxww/reinforcement-learning/pull/73)|Y|`1a7feb942f90`|[s-20261102-13020d89 R001] Public-board upgrade gating: 13 real games, n=4 rank signal only|
|C|[#66](https://github.com/sstxww/reinforcement-learning/pull/66)|Y|`9617c6f93e45`|[s-20261102-0ecd90f7 R001] Real-game public mechanics probe: 240 updates, 5 matches; no rank claim|
|C|[#64](https://github.com/sstxww/reinforcement-learning/pull/64)|Y|`c643fbf41eed`|[s-20261102-73729553 R001] Public-observation masked BC: 95.7% family imitation, 7 real receipts, no rank claim|
|C|[#62](https://github.com/sstxww/reinforcement-learning/pull/62)|Y|`3f452370f502`|[s-20261102-661adf61 R001] Masked teacher BC: 80 updates, 8 real games, no established rank gain|
|C|[#49](https://github.com/sstxww/reinforcement-learning/pull/49)|Y|`3dcc424dbc94`|[s-20261102-8cfa0c44 R001] Real TavernGym multiprocessing throughput ablation: 13 games, slower|
|C|[#44](https://github.com/sstxww/reinforcement-learning/pull/44)|Y|`31adcfe4589d`|[s-20261102-c0039389 R001] Verify seat-sensitive TavernGym full-game evaluation (7 real games)|
|C|[#41](https://github.com/sstxww/reinforcement-learning/pull/41)|Y|`244424b5a8fc`|[s-20261102-221336eb R001] Budget-6 real-game ablation: 12 matches, no decision reduction|
|C|[#36](https://github.com/sstxww/reinforcement-learning/pull/36)|Y|`2c191b5587c2`|[s-20261102-7fd2e223 R001] Idle hero-power paired ablation: pilot gain not reproduced on heldout seeds|
|C|[#35](https://github.com/sstxww/reinforcement-learning/pull/35)|Y|`afeaa5787a74`|[s-20261102-509af6d2 R001] Opening upgrade delay: 40 real games, small uncertain gain|
|C|[#33](https://github.com/sstxww/reinforcement-learning/pull/33)|Y|`4d762dc2eec2`|[s-20261102-6cc5d763 R002] Prebuy refresh: 9 real matches, 32 interventions, exploratory mean rank 6.25|
|C|[#27](https://github.com/sstxww/reinforcement-learning/pull/27)|Y|`e6b2fcab65f3`|[s-20261102-6cc5d763 R001] Genuine refresh ablation: 7 completed games, zero intervention|
|C|[#24](https://github.com/sstxww/reinforcement-learning/pull/24)|Y|`b7da2b3b6652`|[s-20261102-e046f72e R001] Compact PPO extractor + bounded complete-match evaluation|
|C|[#23](https://github.com/sstxww/reinforcement-learning/pull/23)|Y|`9c9969b40100`|[s-20261102-bf8e1710 R001] Test public-observation potential shaping vs sparse PPO reward|
|C|[#22](https://github.com/sstxww/reinforcement-learning/pull/22)|Y|`aa019a2a183a`|[s-20261102-cbc3c4927c R001] Factorized card encoder: 48% card-param savings, complete PPO safety-cap match|
|C|[#14](https://github.com/sstxww/reinforcement-learning/pull/14)|Y|`ba8fb283f67b`|[s-20261102-1d9e7456 R001] Purchase-slot selection bias ablation on real TavernGym|
|C|[#13](https://github.com/sstxww/reinforcement-learning/pull/13)|Y|`30187df4704d`|[s-20261102-04414822 R001] Paired card-embedding width ablation (unverified)|
|C|[#11](https://github.com/sstxww/reinforcement-learning/pull/11)|Y|`9a0f34cd58f0`|[s-20261102-c097d0cc R001] rightmost Play insertion ablation vs baseline|
|C|[#6](https://github.com/sstxww/reinforcement-learning/pull/6)|Y|`71fb0aacf3f5`|[V1][strategy] first-round verified-match candidate|
|D|[#77](https://github.com/sstxww/reinforcement-learning/pull/77)|Y|`d3c7ed72dd01`|[s-20261102-cee57e6a R001] Public-board replacement: 15 authentic games, selected candidate no-op, REJECT|
|D|[#74](https://github.com/sstxww/reinforcement-learning/pull/74)|Y|`0913f2ffae7c`|[s-20261102-aca5a929 R001] Public-card shop ranker: 16 real games, no competitive gain|
|D|[#72](https://github.com/sstxww/reinforcement-learning/pull/72)|Y|`534a31697046`|[s-20261102-1692601b R001] Real sell-swap calibration: 18 games, weak inconclusive rank signal|
|D|[#71](https://github.com/sstxww/reinforcement-learning/pull/71)|Y|`b2bb7b1cee23`|[s-20261102-2d73e890 R001] Bounded blind-sell ablation: 28 real games, heldout rank worse|
|D|[#63](https://github.com/sstxww/reinforcement-learning/pull/63)|Y|`4aeb97e05462`|[s-20261102-4d619f26 R001] Teacher cloning pilot: six real games, no verified gain|
|D|[#61](https://github.com/sstxww/reinforcement-learning/pull/61)|Y|`e683fb6cfe88`|[s-20261102-1f73f4a5 R001] Masked BC on real games: legal imitation, no strength gain (negative pilot)|
|D|[#58](https://github.com/sstxww/reinforcement-learning/pull/58)|Y|`ff40ca8120e2`|[s-20261102-717d0e50 R002] Public-shop Freeze value gating: 30 true games, no observed gain|
|D|[#55](https://github.com/sstxww/reinforcement-learning/pull/55)|Y|`d3f1c8b97e33`|[s-20261102-e9dad467 R002] Held-out 12-game real seat-rotation replication (no policy gain)|
|D|[#52](https://github.com/sstxww/reinforcement-learning/pull/52)|Y|`f88542212941`|[s-20261102-3a93dae9 R001] Hero-power reserve ablation: 28 real matches, no confirmed gain|
|D|[#51](https://github.com/sstxww/reinforcement-learning/pull/51)|Y|`a60fbfbc7133`|[s-20261102-24728f13 R001] PPO learning-rate sensitivity: six real matches, no rank gain|
|D|[#48](https://github.com/sstxww/reinforcement-learning/pull/48)|Y|`5a69719c28de`|[s-20261102-9c034841 R002] Instrumented one-vs-three buy override ablation (negative efficiency result)|
|D|[#42](https://github.com/sstxww/reinforcement-learning/pull/42)|Y|`36bdd4cbc438`|[s-20261102-6cc5d763 R003] Frozen prebuy policy: 16 unseen paired seeds, no confirmed gain|
|D|[#40](https://github.com/sstxww/reinforcement-learning/pull/40)|Y|`f04831ff1057`|[s-20261102-717d0e50 R001] Freeze-at-exit strategy pilot: 20 real games, no observed gain|
|D|[#31](https://github.com/sstxww/reinforcement-learning/pull/31)|Y|`9887e95afc57`|[s-20261102-e599fa38 R001] Guarded PPO termination experiment on real TavernGym (no strength gain)|
|D|[#29](https://github.com/sstxww/reinforcement-learning/pull/29)|Y|`bae4cd16aee1`|[s-20261102-9a484c57 R001] Tavern upgrade-before-play priority: six real games, no gain|
|D|[#28](https://github.com/sstxww/reinforcement-learning/pull/28)|Y|`08304baad4dc`|[s-20261102-2830ac4a R001] Corrected Magnetize action audit: 7 full games, no verified gain|
|D|[#21](https://github.com/sstxww/reinforcement-learning/pull/21)|Y|`3783131213a7`|[s-20261102-2b0d8089 R001] Signed-log reward pilot: negative result, real match receipts|
|D|[#20](https://github.com/sstxww/reinforcement-learning/pull/20)|Y|`8559d3af0249`|[s-20261102-6d2f9a71 R001] Guard PPO free-action loops; paired entropy study (inconclusive)|
|D|[#19](https://github.com/sstxww/reinforcement-learning/pull/19)|Y|`337bdeeb8e74`|[s-20261102-14ce98f3 R001] Test PPO reward scale: 512 real steps, guarded full-game evidence, no gain|
|D|[#18](https://github.com/sstxww/reinforcement-learning/pull/18)|Y|`cd7da5c8aa16`|[s-20261102-e4c71b9d R001] Test masked-mean card pooling (no observed gain)|
|D|[#17](https://github.com/sstxww/reinforcement-learning/pull/17)|Y|`7354e21a17a8`|[s-20261102-1b82df52 R001] signed-log input ablation: 512-step negative pilot|
|D|[#16](https://github.com/sstxww/reinforcement-learning/pull/16)|Y|`63dc7de988f0`|[s-20261102-7f4c9a62 R001] Masked-PPO entropy sensitivity: verified short-run negative result|
|D|[#12](https://github.com/sstxww/reinforcement-learning/pull/12)|Y|`2fad7860f244`|[s-20261102-bedfc382 R001-R002] Potential reward shaping: 8704 PPO steps, 46 full games (negative)|
|E|[#75](https://github.com/sstxww/reinforcement-learning/pull/75)|Y|`19e5cbb46629`|[s-20261102-f3af3b4d R001] Pinned TavernGym card catalog and economy mechanics audit|
|E|[#68](https://github.com/sstxww/reinforcement-learning/pull/68)|Y|`a3ca89fa50b0`|[s-20261102-ada5c379 R001] Pinned native card-mechanism catalog (3983 cards; real-game gate passed)|
|E|[#67](https://github.com/sstxww/reinforcement-learning/pull/67)|Y|`b34cb9505eb9`|[s-20261102-a881710a R001] Pinned-engine static card catalog + real 8-seat public-action probe (no strength clai|
|E|[#50](https://github.com/sstxww/reinforcement-learning/pull/50)|Y|`8ee9b99e1dcb`|[s-20261102-d1116e51 R001] Generic Choose-option index ablation: 7 games, negative pilot|
|E|[#46](https://github.com/sstxww/reinforcement-learning/pull/46)|Y|`0a7d71404a18`|[s-20261102-64405d5e R001] Purchase-before-play priority: 13 real games, gain unproven|
|E|[#45](https://github.com/sstxww/reinforcement-learning/pull/45)|Y|`6333c6831718`|[s-20261102-b34940b0 R002] Hero-selection confound in generic Choose bias (24 real games)|
|E|[#38](https://github.com/sstxww/reinforcement-learning/pull/38)|Y|`c76e0d5a6e3d`|[s-20261102-8555759e R001] Choice-index tie-break ablation: 12 real matches, negative result|
|E|[#34](https://github.com/sstxww/reinforcement-learning/pull/34)|Y|`238ce68e0343`|[s-20261102-9c463177 R001] Real-game mandatory choice tie-break ablation (unverified gain)|
|E|[#32](https://github.com/sstxww/reinforcement-learning/pull/32)|Y|`7f30928a2089`|[s-20261102-b34940b0 R001] Generic forced-choice slot ablation: negative real eight-seat evidence|
|E|[#30](https://github.com/sstxww/reinforcement-learning/pull/30)|Y|`147b02e725eb`|[s-20261102-9c034841 R001] Planned-turn buy-before-upgrade A/B (n=4, gain unproven)|

## CI / merge guardrails

Individual CI check-runs and merge conflict state were **not** fetched for every PR in this snapshot. Therefore no item has been approved for immediate merge. #15 had a successful exact-head check but remains blocked by #9; #8 had no exact-head check when sampled and is conflicted.
Refresh main and each candidate PR SHA, review full diffs and dependency ordering, check latest exact-head CI and real-game receipt, then verify main CI after any merge.
PR #90 has 83 passing unit tests and 4 real 8-seat matches in its own Actions run; initial PR CI failed only due to the then-missing persisted game receipts. Follow-up commit adds authentic compact receipts.

