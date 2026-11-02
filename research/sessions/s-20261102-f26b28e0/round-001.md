# V5 R001 — P0 integration review, P1 paired evidence gate, P2 rank-eight diagnosis

Session: `s-20261102-f26b28e0`  
Base main: `db5e23ae8c218808821327d806b05d2604cfadfb`  
Scope: new namespaced P1 evaluator, regression tests, bounded real TavernGym workflow, and session evidence only.

## P0 — assessed before any changes
- GitHub listed **75 open PRs**; 74 Draft and the only non-Draft #15 targets `agent/learning/v1`, depends on Draft #9 rather than main. No PR safely mergeable immediately in this session.
- Main HEAD `db5e23ae8c218808821327d806b05d2604cfadfb` was green at [full-game CI 41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040).
- Large, overlapping checkpoint and behavior-diagnostic Draft PRs already exist (#93, #91, #86, #103, #105). This branch deliberately does not duplicate or overwrite them. No direct main pushes or model promotion.

## P1 — concrete code change
- New `tavern_ai/paired_receipt_gate_f26b28e0.py` checks canonical real-game receipts, one-to-one heldout seeds, both policy arms, identical engine fingerprints, exact checkpoint SHA256 and registry provenance before calculating paired rank differences.
- Missing fallback telemetry explicitly means **pure model play not verified**; no automatic Champion promotion.
- Independent scoped tests and GitHub Actions real eight-seat baseline canary. No changes to shared `train.yml` or `train.py`.
- Known main `train.yml` limitation: restores only 90-day Artifact; a missing/unavailable Artifact silently restarts from random initialization. This needs a separately owned Release-first workflow integration and validation, not an unsafe direct main edit.

## P2 — source-backed findings and limits
- Canonical registry latest experimental, unpromoted 1408-step checkpoint `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- Three genuine same-seed pairs 99125–99127: model ranks [8,8,8] vs baseline [6,8,8]. Mean 8 vs 7.333; model top-four 0/3. Check source receipts in `experiments/s-20261102-68099929/`.
- Separate authentic public-state opportunity report `reports/s-20261102-68099929/003-buy-opportunity.json`, seed 99128: model had 35 masked-legal BUY decision states, selected BUY zero times; baseline selected 14 BUY in 21 legal-buy states. Both rank eighth on that single seed.
- Another real model trace `reports/s-20261102-ba09e2d4/002-action-opportunities.json`: 5,955 of 6,000 decisions were HeroPower/Cancel, 10 masked-legal BUY states and no BUY; **failed to complete**, so NOT a valid ranked result. The loop failure is observable, but its causal contribution to rank remains undetermined.
- Therefore hypothesis: policy overuses low-progress action loops and neglects legal purchases. This is not yet proof of which learning mechanism (masking, reward, observation, PPO optimization, game state) caused it, and every legal BUY is not automatically strategically good.

## Validation / honest remaining gates
- Branch isolated code and CI run required; status updated in STATUS.md after run. This agent trained **0 PPO steps**, promoted **0 models**, entered **0 Arena games**.
- If current branch's real-game artifact is available, it must be copied and independently verified into `experiments/s-20261102-f26b28e0/` before PR may be marked ready for integration.
- Next high-priority work: Release-first durable restore in main train workflow via separate integration review; per-turn progress and legal-buy denominator audit on latest 1408-step checkpoint; one-factor intervention, then only bounded PPO resume after quality gates.
