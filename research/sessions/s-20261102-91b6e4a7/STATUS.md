# V5 P0/P1 registry integration — smoke passed, main conflict reconciled

Session s-20261102-91b6e4a7; own branch `agent/s-20261102-91b6e4a7/optimization-001`.
Original main base: `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`. PR: https://github.com/sstxww/reinforcement-learning/pull/93

**Main integration reconciliation:** Concurrent PR #87 merged a canonical `models/registry.json` at `c85d566cccccf5e2ef7de09b6cc95e1aa506da9c`. Our branch's registry bytes were updated to MATCH that exact main blob (SHA `2467e05303fce700f6102a129bd77987819eda3e`) so our PR no longer introduces a second registry. The existing main registry tracks four unpromoted releases; its "latest" means the latest **experimental**, not a verified recovery checkpoint. `best` and `champion` are null.

**Original actual engine evidence:** GitHub Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41427822784 SUCCESS. Pinned 1.1.0 and old isolated catalog tests passed; baseline controlled seat 0 seed 91031 rank 8; 14 turns, 51 decisions, placements [8,1,5,2,6,3,4,7], complete true, zero truncation. Genuine receipt `experiments/s-20261102-91b6e4a7/001-91031.json` commit `65bf5ccc1a9f1dfaf7d9fef8aef7f95964cd4826`.

**Current integration delta:** `tavern_ai/checkpoint_catalog.py` checks GitHub-reported metadata SHA256 (four releases), checkpoint SHA256 using main registry integrity module, ZIP member CRC, metadata engine fingerprint and accumulated timesteps. `tests/test_checkpoint_catalog_91b6e4a7.py` covers corruption and unsafe promotions. Neither tool loads a PPO model or proves restore. Latest PR-head CI is required again after adapting to PR #87.

**Research honesty:** 0 PPO steps and 0 model-only games this session. No new weights or champion. No official Arena match. Rank-8 model root-cause remains unknown; issue #78 has low-buy vs repeated-action symptoms, not affordable-buy/no-progress causality. No large-scale PPO justified.
