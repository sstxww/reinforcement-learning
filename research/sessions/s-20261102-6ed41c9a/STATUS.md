# V5 independent session status — s-20261102-6ed41c9a

Round: 001. Base: main `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
Task: P0 integration audit; P1 registered Release recovery + durable model custody; P2 classify rank-eight evidence.
P0 scan: 75 open PRs, 74 Draft, only non-Draft #15 stacked on Draft #9. No unreviewed merge.
P1 code committed on own isolated branch: registered Release-tag selection; SHA256 and engine/ZIP/step gates; optional manual main resume; successful training full-game/eval before durable Release with redownload; no Champion promotion.
P2 main evidence: latest registered 1408-step experimental candidate, rank 8, 35 masked BUY legal decisions but 0 BUY choices on seed 99128; one-game causal proof NOT established.
Own proof workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41450122083 — pending when written. Must inspect logs and commit **real** receipt before PR review.
Real PPO steps this session: 0. New weights: none. Ranked Arena: 0. Main mutated: no.
Review required: new training workflow contents:write permission, final-head PR CI, exact main merge SHA and post-merge CI. Never claim successful integration without these.

## Verified complete-game evidence and save recovery
Own Action [41450088225](https://github.com/sstxww/reinforcement-learning/actions/runs/41450088225) executed 15 new regression tests successfully and built pinned TavernGym 1.1.0. Real baseline-controlled eight-seat game seed 94311 completed (rank 8, 15 turns, 40 actions, 0 truncated combats, no turn-limit ending). Its final receipt was originally printed by the engine and validated. The run FAILED only at git push because this branch advanced concurrently. Extracted the **exact actual JSON** from the authentic run's job log and committed it to `experiments/s-20261102-6ed41c9a/001-94311.json` in commit `5f8f7714225c43e259f015d17c52b0de73ff7cb9`. Updated isolated workflow with remote rebase/receipt-preservation guard (commit `81648c5d67da8c257fdadb3e69f3e4e8bcbc47d0`), avoiding forced updates. Current proof workflow and PR CI must still be checked on **new final heads**. This was BASELINE not a model/game quality claim.
