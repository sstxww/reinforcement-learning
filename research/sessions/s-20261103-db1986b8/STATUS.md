# STATUS — s-20261103-db1986b8

State: **review_pending** for [PR #164](https://github.com/sstxww/reinforcement-learning/pull/164). Safe concurrent main sync performed from `df07dd23c99079449417fa8e645cf2b6c76b9704`; historical branch code replaced rather than overwrite already-integrated shared train.yml.

Initial main: `9685cc33c0f05821de3e0a8d2997aedeb3725500`, passed CI 41506832439. Initial P0 snapshot: 115 open PRs (114 Draft), #15 stacked on Draft #9. Since then other integrators merged #116/#117/#125/#138/#154; this session **does not claim those merges**. Current main has reliable Release restore, staged checkpoint checksum, evidence-gated Champion and manual-only train workflow. The originally proposed replacement train.yml was superseded and is NOT part of this PR's final diff.

This session's focused P1 delta: preserve full schema-2 compatibility and `increment_timesteps` when continuing a real checkpoint, rather than rewriting all resumed files as schema-1. Reject corrupt/unknown schema-2 provenance and invalid training-step deltas. Added synthetic-only regressions; no new model-weight or competitive claim.

Own real pinned TavernGym baseline [Actions #41507827256](https://github.com/sstxww/reinforcement-learning/actions/runs/41507827256) succeeded: original `experiments/s-20261103-db1986b8/001-931281.json`, SHA256 `ff9c0c8489884955d59a54874c6fa8f596551a410780cf6630e3714d7c64133d`; seed 931281, rank 6, 15 turns, 55 decisions, complete, 0 combat truncations. Infrastructure only; no own PPO training.

Model registry best/champion null, latest unpromoted 1408-step Release `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, heldout [8,8,8] vs baseline [6,8,8].

P2: PR #103 legal buy opportunities ignored, #107 forced 46 Buys yet [8,8,8] with Play/Cancel loops, #156 raw V5 Refresh/Freeze cycling and incomplete game. Root cause partly unresolved.

**Still unfulfilled in this session:** raw PPO game 0, additional train steps 0, new weights 0, stored new models 0, no Champion promotion, no Arena. Keep Draft until exact-head CI, security review and true schema-2 model resume if needed; tests are synthetic.
