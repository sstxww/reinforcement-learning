# R001 — fail-closed paired evaluation receipt integration

## Scope and source
Session `s-20261102-1aff5449`; isolated branch `agent/s-20261102-1aff5449/optimization-001` from main `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`. Source audit: `tavern_ai/evaluate.py`, `tavern_ai/receipt_integrity.py`, `tavern_ai/canary.py`, `tests/test_evaluation_v1.py`. TavernGym pinned expected contract 1.1.0 / hash `6d8712c93022ba11` / observe2 4017 numeric + 447 card IDs / 245 actions.

## Verified source problem
The shared `evaluate()` path summarized final placements from `run()` without verifying receipt integrity before reporting. Future runner changes or tampered records could therefore be counted as authentic games. The `summarize()` helper divided by zero for empty batches. This is an engineering metric-integrity bug, not an established root cause of rank-8 model play.

## Change and synthetic regressions
Use existing strict receipt validator for complete eight-seat source/seed/policy/model hash. Require the exact same heldout seed list for candidate and baseline, constant checkpoint digest within a candidate batch, controlled seat 0 and no guard/fallback counts. Reject empty record summaries. Add offline synthetic negative tests, explicitly not presented as actual TavernGym games.

## Genuine evaluation and training status
Real engine-backed run [41450193460](https://github.com/sstxww/reinforcement-learning/actions/runs/41450193460), job 125293203851: independent baseline seat0 game seed 91991 **completed**, rank **8**, turns 18, decisions 38, placements [8,3,2,7,5,1,6,4], truncated combats 0, turn-limit end false, exact TavernGym source hash 6d8712c93022ba11. Offline tests and genuine game verification passed. The run status is **FAILURE** because the final git push was non-fast-forward when concurrent session docs advanced. A fetch/rebase fix triggered run [41450862282](https://github.com/sstxww/reinforcement-learning/actions/runs/41450862282), no success asserted until confirmed. Actual receipt was copied from the first run's raw **machine-generated JSON stdout** (parsed and strictly checked, not fabricated) and committed via repository contents API to `experiments/s-20261102-1aff5449/001-91991.json` at `38d9ccdc5436f10c2b3c5c35b0c488525ec1ed07`. This is authentic **baseline engineering evidence**, not PPO candidate evaluation. No PPO training, checkpoint publication, candidate promotion or scored Arena match. Expected baseline game is only engineering evidence, not a claim of model improvement.

## P0 integration review
Snapshot: 75 open PR; conflicting and stacked drafts excluded from automatic merge. PR #15 points to branch `agent/learning/v1` (#9 prerequisite). Non-draft #102 reported mergeable=false when inspected; other V5 checkpoint/behavior PRs mainly Draft. Main moved while other agents were merging, so do not assume this snapshot stays current. Work in isolated branch; do not push main.

## Acceptance and follow-up
Require actual eight-seat game with `Game.is_over()`, no truncation, strict validator, exact-head CI, human diff/security review and recheck main SHA before any merge. This patch improves evidence integrity only. Follow-up P1: replace Artifact-only silent cold-start in main train.yml with explicit durable-release, hash-verified fail-closed recovery. Follow-up P2: separate raw PPO from guard performance and diagnose observed Buy/Play/Cancel nonprogression with legal opportunities.

## Experimental counts
Actual PPO steps by this session: **0**. Real games verified by this session (baseline only): **1**. Candidate-vs-baseline pairs: **0**. New model files: **0**.
