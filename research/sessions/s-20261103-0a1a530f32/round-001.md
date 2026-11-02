# Round 001 — truthful V7 merge-exclusivity regression

Session `s-20261103-0a1a530f32`; task `p0/v7-main-integration-entry`; base `main@c1b828734527bae6141805581693d890cc3bff94`; role REPAIRER / REVIEWER; dedicated task-claim ref `claims/p0-v7-main-integration-entry-001`.

## Inherited evidence and falsifiable hypothesis
- [Issue #182](https://github.com/sstxww/reinforcement-learning/issues/182) demonstrates a concrete violation: a legitimate CAS coordination ref for PR #164 was held, yet another merge writer updated main. **Task branch/ref ownership != globally exclusive merge rights.**
- Already merged [PR #165](https://github.com/sstxww/reinforcement-learning/pull/165) introduced a separate privileged Release publisher; avoid competing edits to `.github/workflows/train.yml`. [PR #175](https://github.com/sstxww/reinforcement-learning/pull/175) is an active draft no-clobber restore fix, not ours.
- Hypothesis: a read-only snapshot explicitly checking both observed main heads, expected main/head SHA, Draft/mergeability, exact-head CI and server-side enforcement evidence can prevent **false merge authorization** in audit reports. It cannot physically stop bypassing writers.

## Implemented and checked
- New isolated `scripts/v7_merge_safety_0a1a530f32.py` queries GitHub read-only with full expected SHAs; reports `merge_authorized=false` even if a user-supplied flag claims enforcement.
- New `tests/test_v7_merge_safety_0a1a530f32.py`: 7 local focused pytest tests PASS on worktree; cases: good structural snapshot still no merge, unprotected main, main changes during review, stale PR head, stacked PR, Draft/dirty/no-CI and invalid SHA.
- Own read-only one-shot Action [41513118163](https://github.com/sstxww/reinforcement-learning/actions/runs/41513118163) scheduled to run actual engine + eight-seat baseline seed 998803. Its game is **not complete merely because queued**. Extract and check runner evidence before saving any `experiments/` completed JSON.
- No production code in `train.yml`, no model registry edit, no writes to another session's branch, no ranked Arena or direct merge.

## Known limits
- Current main branch metadata at inspection: `protected=false`; protection API from connector responds 403; no independently enforced queue known.
- This is deliberately **not a server-side mutex**, merge automation, or training improvement. Required future action is an enforced queue or sole nominated integrator; remove bypass paths, test adversarial concurrent merge attempts, and then enforce required head/base/CI/reviews.
- This session trained **0 PPO steps**; published **0 new model releases**; fresh raw-model paired evaluation **n=0**. Existing 1408-step V5 source SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` remains unpromoted and the rank-8/economic liveness problem persists.

## Next
Inspect own run's actual job and JSON evidence, then commit only verified genuine baseline receipt. Update PR with exact head & CI gate. No `main` merge without global exclusivity.
