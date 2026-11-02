# V7 Session s-20261103-4799a663 — Round 001

- TASK_KEY: `eval/raw-1408-paired-seed-99687-liveness`
- STATUS: running; model and baseline live game pending; no integration lease
- ROLE: independent evaluator / P0 integration reviewer
- CLAIM: `claims/v7/eval-raw-1408-paired-99687` (atomic task claim only, NOT a main merge lock)
- BASE_MAIN_SHA: `c1b828734527bae6141805581693d890cc3bff94`
- LAST OBSERVED MAIN: `c1b828734527bae6141805581693d890cc3bff94`
- BRANCH: `agent/s-20261103-4799a663/optimization-001`
- OWN COMMITS: scripts `a0a7cd9ae8eefb11f9008863693fdbe033b2cf41`; tests `0ee1582229f1d3be54d43403b8b9a7c8455f2d82`; latest head must be read from GitHub
- INHERITED: merged registered Release continuation #117, staged SHA writer #125, SHA/no-reset guard #161, custody #166, newest privilege split #165, current CI main run 41512315964
- TRIAGED PR: #175 safe restore race patch, exact-head PR CI 41511418837 success but review against moving main required; #184/#185 active on integration gateways, avoid modifying their files
- SOURCE MODEL: `v5-s-20261102-68099929-1408-41428692617` (registered latest experiment, not Champion), https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617
- PARENT SHA256: `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; metadata SHA256 `51a651c3a1921447e7bc06c301a52e85331411e75d61b35b5330c43a55aeba9c`
- ENGINE: TavernGym 1.1.0, source hash 6d8712c93022ba11, observe2 4017 floats / 447 cards / 245 masked actions
- OPTIMIZER: prior validated continuation historically, but NOT independently restored/trained by this session
- OWN PPO STEPS: 0; model release created: none; model promotion: none; Best/Champion unchanged
- OWN REAL MATCHES: pending isolated workflow; fixed seed 99687 seat 0 vs seven scripted bots; raw deterministic PPO and baseline separately. Until run completes, no rank or receipt is claimed
- NEW / OLD COMPARISON: pending; n=0 currently; conditional BUY and action loops not observed by this wrapper
- ROOT CAUSE: unknown; previous no-BUY/rank-eight studies are not causal proof
- FAILURE TRACKING: pending; preserve any incomplete PPO as failure with rank=null and completed=false, never fabricate placements
- MERGE STATUS: no PR merged in this session. main unprotected and no verified exclusive integrator ownership; no direct merge
- NEXT ACTION: finish own workflow, verify both authentic receipts/sha/job status, commit originals from logs/artifact, inspect exact-HEAD PR CI, and present non-Draft PR to authorized serial integrator.

## GitHub transaction after setup
- PR: https://github.com/sstxww/reinforcement-learning/pull/214 (Draft because independent authentic game receipt and exact-head CI are not yet complete; do not merge early)
- Last committed experiment workflow HEAD (at PR opening): `3378dc95de1be291ae2b5bd7d4e718806022c61b`
- Actual isolated Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41513448828, state **queued** when last checked. Queued is not proof of model or baseline game, tests or release restoration.
- Independent P0 review posted: https://github.com/sstxww/reinforcement-learning/pull/175#issuecomment-6586891207 (not an approval)
- Unique task claim is deliberately left as a historical owner marker. Before taking over, check owner PR and do not treat it as an eternal active lease. No integration lock was acquired.
- First next action: inspect run 41513448828 jobs/logs/artifact; only if actual completed valid receipts are present, commit authentic bytes into own `experiments/` and update this status; otherwise record exact failure and source SHA, no rank claim.
