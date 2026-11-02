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

## Latest authoritative R001 result (supersedes earlier queued/pending snapshots)
- STATE: `ready_for_CI_review` (real match and source digest verified; latest-head PR CI and independent review still pending). No exclusive main integrator.
- SESSION: `s-20261103-4799a663`; TASK_KEY: `eval/raw-1408-paired-seed-99687-liveness`.
- BRANCH: `agent/s-20261103-4799a663/optimization-001`; PR [#214](https://github.com/sstxww/reinforcement-learning/pull/214), currently Draft pending exact-head CI.
- BASE_MAIN_SHA and last observed main: `c1b828734527bae6141805581693d890cc3bff94`; postmerge main [CI 41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964) completed SUCCESS for that SHA. Refresh before any integration.
- Verified original run: [41513448828](https://github.com/sstxww/reinforcement-learning/actions/runs/41513448828) completed SUCCESS, branch-run HEAD `3378dc95de1be291ae2b5bd7d4e718806022c61b`, job `125510847500`, 11 tests passing, native engine pinned, official Release bytes SHA verified, CPU model load successful.
- Original [Artifact 13175291485](https://github.com/sstxww/reinforcement-learning/actions/runs/41513448828/artifacts/13175291485) ZIP SHA256 `f28332a6bbc6776de26bd137c7c599b32b0a3322d2f112458168de7067e16349` temporary 30-day; all three JSONs are now copied *byte-for-byte* and verified via Git blob SHA against the original zip:
  - `experiments/s-20261103-4799a663/001-99687-model.json`: raw model, complete rank **8**, placements [8,3,2,1,7,5,4,6], 14 turns, 122 decisions, original SHA256 `e1047e3a2a4b39a64089de45f37388367b2c7867b1309bf02a552422e433d55a`.
  - `experiments/s-20261103-4799a663/001-99687-baseline.json`: baseline, complete rank **8**, placements [8,4,3,7,5,2,1,6], 13 turns, 43 decisions, original SHA256 `ab38b05e67e5f092c1b5c7c333bdd1ab9e1fbcd93745c3ab6a2186fadf42f1d4`.
  - `experiments/s-20261103-4799a663/001-99687-status.json`: paired n=1 and rank delta **0**, original SHA256 `6fe0ca5fd0ca8b8c841ae9240e5be11f16a44a819959ca959fb24f5d7ebf3cd9`.
- Inference identity: registered 1408-step unpromoted Release [tag](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617), weight SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Independent optimizer resume by this session: NO. Own new PPO steps=0; new Release=0; model promotion=0; merged PR=0.
- Proven: original and downloaded source model match registry, both matches naturally complete without truncated combat, same seed rank8 baseline+raw. Not proven: causal no-BUY reason, strategy improvement, generalization, statistically equal strength.
- Handoff first step: inspect **latest PR #214 head** and exact-head CI run, validate changed receipt integrity against original Artifact; if green, independent review -> mark ready; integrate only through globally enforced exclusive main merge path, expected head SHA and verified latest-main CI. If CI fails, read actual failed job logs and patch only own branch; keep receipts unchanged. No duplicate Actions spam.
- No main merge lease acquired; deterministic task claim remains for historical ownership; other sessions must respect the owner and only use an explicit handoff.
