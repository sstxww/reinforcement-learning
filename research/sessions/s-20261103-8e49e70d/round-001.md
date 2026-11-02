# Round 001 — scoped Actions triggers, not full model training

**V7 protocol:** latest 32,014-byte Gmail TXT fully read. **Start:** main `c1b828734527bae6141805581693d890cc3bff94`. Acquired deterministic task branch `claims/v7/session-workflow-trigger-scope` (no right to merge main).

## Prior art and hypothesis

Read main core protocols, canonical training and CI workflows; current main CI [41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964) succeeds. PR [#184](https://github.com/sstxww/reinforcement-learning/pull/184) has a session-specific workflow including unfiltered `pull_request:`; PR [#185](https://github.com/sstxww/reinforcement-learning/pull/185) addresses a cooperative serial merge gateway but does not enforce global GitHub REST merge exclusivity. Many legacy session workflows are intentionally push-scoped. **Hypothesis:** unfiltered PR events on session-only workflows can cause unrelated PRs to run unnecessary experiments; static detection makes total Actions cost visible.

## Implement and test

- `scripts/v7_workflow_trigger_scope_8e49e70d.py` reads session-specific workflow YAML `on` keys, without executing workflow scripts. It flags unfiltered pull_request, unscoped push, pull_request_target and schedule/workflow_run. Does not change any other workflow.
- `tests/test_v7_workflow_trigger_scope_8e49e70d.py`: six synthetic regression tests, including inline YAML events, pull_request base-branch illusion, narrow path filtering, and YAML-like data inside shell scripts.
- Local first test: 5 passed, 1 failed due to event-token regexp not recognizing `on: [push, pull_request]`. Fixed tokenization; second execution: **6 passed**, compiled successfully. This is a real local bug fix, NOT a TavernGym result.
- Own workflow `.github/workflows/trigger-scope-s-20261103-8e49e70d.yml`: uniquely scoped branch/path trigger, fixed concurrency group, read-only token, timeout 70 minutes, no automatic push/merge. Runs tests + live repository audit + TavernGym 1.1.0 full baseline seed 99783 and saves original evidence as expiring Artifact.

## Evidence pending

Actual branch run [41513652959](https://github.com/sstxww/reinforcement-learning/actions/runs/41513652959), head `c468573aedc8d18997d9fe082de54e53a6a0a41b` was queued when checked. Placement, receipt, observed workflow warnings and Actions job outcome **unknown** as of this initial report. No claimed PPO steps, new model, released checkpoint, paired model results, PR merge, or Champion promotion. Official registered V5 1408-step experimental model has no verified competitive gain; its Release SHA256 is `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.

## Next

If run succeeds, retrieve original artifact, validate and commit own receipt and observed audit with exact values; then submit non-Draft PR, get exact-head CI and independent review; main merge only through proven exclusive executor. If the run fails or is action_required, record exact error and fix, never count queue as match.
