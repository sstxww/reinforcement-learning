# Round 001 — scoped Actions triggers, not full model training

**V7 protocol:** latest 32,014-byte Gmail TXT fully read. **Start:** main `c1b828734527bae6141805581693d890cc3bff94`. Acquired deterministic task branch `claims/v7/session-workflow-trigger-scope` (no right to merge main).

## Prior art and hypothesis

Read main core protocols, canonical training and CI workflows; current main CI [41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964) succeeds. PR [#184](https://github.com/sstxww/reinforcement-learning/pull/184) has a session-specific workflow including unfiltered `pull_request:`; PR [#185](https://github.com/sstxww/reinforcement-learning/pull/185) addresses a cooperative serial merge gateway but does not enforce global GitHub REST merge exclusivity. Many legacy session workflows are intentionally push-scoped. **Hypothesis:** unfiltered PR events on session-only workflows can cause unrelated PRs to run unnecessary experiments; static detection makes total Actions cost visible.

## Implement and test

- `scripts/v7_workflow_trigger_scope_8e49e70d.py` reads session-specific workflow YAML `on` keys, without executing workflow scripts. It flags unfiltered pull_request, unscoped push, pull_request_target and schedule/workflow_run. Does not change any other workflow.
- `tests/test_v7_workflow_trigger_scope_8e49e70d.py`: six synthetic regression tests, including inline YAML events, pull_request base-branch illusion, narrow path filtering, and YAML-like data inside shell scripts.
- Local first test: 5 passed, 1 failed due to event-token regexp not recognizing `on: [push, pull_request]`. Fixed tokenization; second execution: **6 passed**, compiled successfully. This is a real local bug fix, NOT a TavernGym result.
- Own workflow `.github/workflows/trigger-scope-s-20261103-8e49e70d.yml`: uniquely scoped branch/path trigger, fixed concurrency group, read-only token, timeout 70 minutes, no automatic push/merge. Runs tests + live repository audit + TavernGym 1.1.0 full baseline seed 99783 and saves original evidence as expiring Artifact.

## Verified independent GitHub Actions evidence

The actual independent [run 41513652959](https://github.com/sstxww/reinforcement-learning/actions/runs/41513652959), head `c468573aedc8d18997d9fe082de54e53a6a0a41b`, completed **SUCCESS**. Real job `125511540046` steps passed regressions, live static scan, pinned TavernGym 1.1.0 bootstrap/contract, complete seed **99783** baseline seat 0 vs seven bots, and artifact upload. Original independent full-game [Artifact 13174297357](https://github.com/sstxww/reinforcement-learning/actions/runs/41513652959/artifacts/13174297357) downloaded and inspected: `completed=true`, **rank8**, placements `[8,2,3,6,1,5,7,4]`, turns=15, decisions=33, `truncated_combats=0`, `turn_limit_end=false`, SHA256 `5d9d5045fab0a988707c9ba29f1fbb9759a881086bade1ceb9bb6e807b0fc42b`; original 516 bytes committed unchanged at `experiments/s-20261103-8e49e70d/001-99783.json` in commit `3faad589c741e405cdd002656cb3261a240aa8de`. **This is baseline infrastructure smoke, not raw PPO.**

From the same Artifact, original audit JSON SHA256 `37fdb87f722dfb2524ac71d1ece762a20c9310cb984a2aac07a6b9d406f70dff`: 43 workflows scanned, 30 session-named workflows, 0 current flagged cases; committed `reports/s-20261103-8e49e70d/001-trigger-scope.json` in commit `512515416a4e8541e092b1d26cb4161e15a84921`. This snapshot does not imply future runs are safe, measure past unused Actions, or prove spending reduction.

The one-shot runner was removed from eventual PR code in commit `4e1007a34b55fbd0aa8e7ef88f83e7d671c42767` to avoid long-term workflow proliferation. This does not delete the real historical Action, log or artifact (30-day Artifact, committed immutable JSON in Git). 0 new PPO steps, 0 optimizer resumes, 0 model-controlled games, 0 Release, no Best/Champion promotion or ranked Arena; prior V5 latest unpromoted 1408-step checkpoint SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` was not downloaded by this session.

## Next

Original evidence now committed. Submit **non-Draft PR**, verify latest-head PR CI's own true eight-seat job, then independent review/merge-compatibility checks. No main merge without globally exclusive integration entry; exact-head green is required but insufficient for main merge.
