# 001 — PR evidence gate correctly blocked missing authentic receipt

- Failure class: incomplete source evidence; NOT Python algorithm test failure or engine problem.
- Failing URL: https://github.com/sstxww/reinforcement-learning/actions/runs/41512555970
- PR source HEAD then: `58073fd1157e84769e9f47bdead39584191216c4`.
- Job: `tests-and-full-match`, first failing step `Unit tests and PR evidence`.
- Exact failure signature: `Missing independent agent game receipt`.
- Upstream tests: 390 passed, 1 skipped. CI full game step skipped as expected after evidence gate failure.
- Proven root cause: no committed `experiments/s-20261103-d3d410f5/*.json` yet. GitHub Artifact alone cannot satisfy repository's separate source-receipt gate.
- Fix: independent Actions run #41512407251 completed actual TavernGym baseline seed 99673; original Artifact 13174146377 read and checked, then JSON committed unchanged as `experiments/s-20261103-d3d410f5/001-99673.json`, bytes SHA256 `72e4c7094af59f7b2c551c8f5f3f18d6b115fcb36141409bc9fa3cff4655286e`.
- Fresh PR CI: pending; do not claim fix passed until exact latest HEAD check is green.
- Remaining: independent review and genuine safe merger gateway adoption; no PPO steps or model claims.
