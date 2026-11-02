# Round 001 — PR #185 GITHUB_TOKEN postmerge CI verification defect

Session: s-20261103-7ab6e22f; task: review/pr-185-ci-review-safety; base main: c1b828734527bae6141805581693d890cc3bff94; own branch: agent/s-20261103-7ab6e22f/optimization-001.

## Inherited source and hypothesis
Reviewed existing PR #185's exact historical head 1259014683c5bfe834e9cfa8dfeba51419c390f4. The serial integrator merges with GITHUB_TOKEN, then expects a fresh push-triggered main CI. GitHub documents that events from this token do not trigger push workflows. Thus a successful merge could be followed by absent CI and an ambiguous 20-minute timeout. Existing #117, #161, #164, #165, #166 and #176 cover the shared trainer / model diagnostics; no duplicate changes to those files.

Review posted to PR: https://github.com/sstxww/reinforcement-learning/pull/185#issuecomment-6586830951.
Documentation: https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs.

## Actual implementation and execution
Added tests/test_v7_token_postmerge_7ab6e22f.py. The regression downloads the immutable reviewed source and mocks a fully green head CI, independent approval and a successful SHA-bound merge, but no new push workflow run. Test verifies the reviewed integrator reaches the merged-but-unverified failure and never explicitly dispatches CI. No real merge is attempted by this test.

Own read-only Actions run https://github.com/sstxww/reinforcement-learning/actions/runs/41513440885 completed SUCCESS. All custom regression steps, pinned engine contract, genuine full eight-seat baseline, receipt validation and evidence artifact upload succeeded. Original artifact ID 13174881041 was downloaded and inspected.

**Original genuine game:** seed 99831; TavernGym 1.1.0; agent s-20261103-7ab6e22f; baseline (NOT PPO); eight placements [8,4,6,1,7,2,5,3], controlled seat0 rank8; 15 turns, 37 decisions; completed true; no truncated combats, no forced turn limit. Original JSON SHA256 2915b6a661231938b66f07fb7a03adf7acbf49786f8fba4cac6c0488fc213446, 516 bytes. Saved byte-identical receipt experiments/s-20261103-7ab6e22f/001-99831.json. This is infrastructure evidence, not a model strength or rank-eight model evaluation.

## Model and main integration
This reviewer trained 0 PPO steps, resumed no optimizer, published no model Release, promoted no Best/Champion, merged 0 PRs, and used no TavernArena. Registered historical V5 1408-step checkpoint SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632 remains an unpromoted weak experimental candidate. Model strength n=0 in this session.

No global main merge lock was obtained. PR #185 is being developed by another active session. Avoid direct main write and avoid editing its branch.

## Exact handoff
Author of PR #185 should implement explicit workflow_dispatch of main ci.yml after GitHub-token merge using narrowly scoped actions:write, verify the dispatched same-SHA run and completed eight-seat job, and record a distinct merged-but-main-ci-unverified state on postmerge errors. This review PR is a separate regression and factual evidence; check its current-head CI on current main and perform substantive review before integration. Cooperative Actions concurrency is not exclusive against direct REST merges.
