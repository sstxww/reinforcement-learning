# R001 — fail-closed paired evaluation receipt integration

## Scope and source
Session `s-20261102-1aff5449`; isolated branch `agent/s-20261102-1aff5449/optimization-001` from main `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`. Source audit: `tavern_ai/evaluate.py`, `tavern_ai/receipt_integrity.py`, `tavern_ai/canary.py`, `tests/test_evaluation_v1.py`. TavernGym pinned expected contract 1.1.0 / hash `6d8712c93022ba11` / observe2 4017 numeric + 447 card IDs / 245 actions.

## Verified source problem
The shared `evaluate()` path summarized final placements from `run()` without verifying receipt integrity before reporting. Future runner changes or tampered records could therefore be counted as authentic games. The `summarize()` helper divided by zero for empty batches. This is an engineering metric-integrity bug, not an established root cause of rank-8 model play.

## Change and synthetic regressions
Use existing strict receipt validator for complete eight-seat source/seed/policy/model hash. Require the exact same heldout seed list for candidate and baseline, constant checkpoint digest within a candidate batch, controlled seat 0 and no guard/fallback counts. Reject empty record summaries. Add offline synthetic negative tests, explicitly not presented as actual TavernGym games.

## Genuine evaluation and training status
A separate finite GitHub Actions run is required to commit this session's real baseline-controlled eight-seat receipt under `experiments/s-20261102-1aff5449/`. At this document commit: not executed or verified, rank unavailable. No PPO training, checkpoint publication, candidate promotion or scored Arena match. Expected baseline game is only engineering evidence, not a claim of model improvement.

## P0 integration review
Snapshot: 75 open PR; conflicting and stacked drafts excluded from automatic merge. PR #15 points to branch `agent/learning/v1` (#9 prerequisite). Non-draft #102 reported mergeable=false when inspected; other V5 checkpoint/behavior PRs mainly Draft. Main moved while other agents were merging, so do not assume this snapshot stays current. Work in isolated branch; do not push main.

## Acceptance and follow-up
Require actual eight-seat game with `Game.is_over()`, no truncation, strict validator, exact-head CI, human diff/security review and recheck main SHA before any merge. This patch improves evidence integrity only. Follow-up P1: replace Artifact-only silent cold-start in main train.yml with explicit durable-release, hash-verified fail-closed recovery. Follow-up P2: separate raw PPO from guard performance and diagnose observed Buy/Play/Cancel nonprogression with legal opportunities.

## Experimental counts
Actual PPO steps by this session: **0**. Real games verified by this session at document creation: **0**. Candidate-vs-baseline pairs: **0**. New model files: **0**.
