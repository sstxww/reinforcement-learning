# R001 — Prevent stale CI from authorizing main integration

## Proof from live GitHub API
- Read complete AutoTavern V7 Gmail TXT and current main `c1b828734527bae6141805581693d890cc3bff94`.
- CI run https://github.com/sstxww/reinforcement-learning/actions/runs/41511418837 reports `pull_requests[0].base.sha=70c411b64034c8f66618811ff7a98914395735a5`, although the observed current main is `c1b828734527bae6141805581693d890cc3bff94`.
- Existing PR #185 `check_run` compares a workflow run's start time to main's committer timestamp, not its bound base SHA. That admits queued jobs which started late despite having an older synthetic merge base.
- Actual GitHub review comment: https://github.com/sstxww/reinforcement-learning/pull/185#issuecomment-6586826368

## Code and experiment
- Offline exact-base verifier rejects missing/ambiguous PR bindings, mismatching head/main SHA, unrelated workflow, incomplete/failed job run.
- Synthetic regression suite: 15 locally executed tests passed (not model performance or a substitute for GitHub CI).
- Separate finite Actions on own branch: pinned TavernGym genuine eight-seat **baseline** seed 99679 intended; result and placement remain unverified until Actions and the original receipt are inspected.
- No new training, optimizer restore, persistent checkpoint, Release, raw PPO evaluation or Champion promotion in this round.
- No main merge: Issue #182 documents cooperative CAS bypass; observed main was `protected=false`; no enforced global exclusive gate established.

## Follow-up integration requirements
1. Once own real baseline receipt succeeds, commit its original bytes under this session, and check exact-head PR CI.
2. Move the tested exact `run.pull_requests[].base.sha` precondition into the single chosen gateway (#185), avoiding competing gate entrypoints.
3. Main merge remains blocked until a truly enforced serial entry, current-base merged-code CI and independent review all pass.
