# R001 — CI workflow source trust boundary

## Existing work and precise hypothesis
Read V7 TXT (32,014 bytes), main CI #41512315964 and PR #185 source code/CI logs. Its `check_run` and `check_jobs` use workflow path, job/step names and conclusions to infer that tests/engine/real game executed. A PR might alter its own CI workflow while preserving the same public names. **Hypothesis, not an observed malicious attack**: success by step-name alone is insufficient for trust. The independent gate should detect edits to the trusted workflow/critical scripts on both renamed-from and renamed-to paths.

## Implementation
Own only `scripts/v7_ci_definition_guard_223b16589f.py`, `tests/test_v7_ci_definition_guard_223b16589f.py`, session-specific one-shot workflow and session evidence. Read-only GitHub REST retrieval with exact main/head SHA, two identity checks, full changed-file pagination and a deliberately conservative CI trust-boundary denylist. Test rename, tampered CI, duplicate/malformed paths, pagination, concurrent head/main change. Expose no merge writes and no tokens in logs.

## Original evidence and budget
- Main@start `c1b828734527bae6141805581693d890cc3bff94`; CI #41512315964 SUCCESS.
- PR #185: HEAD `a07bd90d2ce886f9cdf54263ed44b81a2d28b212`, CI #41512690022 failed at *Missing independent agent game receipt*, after 390 passed/1 skipped. Parent game run #41512683244 was queued on inspection.
- Task claim `claims/v7/ci-workflow-integrity` creation succeeded atomically; it is **not** a global merge lease.
- Own workflow: smoke budget one baseline eight-seat seed `99681` with TavernGym 1.1.0, separate from model; finite 40-minute limit; no model training. **Completed SUCCESS** in [Actions #41513747112](https://github.com/sstxww/reinforcement-learning/actions/runs/41513747112); all 11 job steps green. Original artifact `13174352630`; receipt SHA256 `4e2f9c8a9dc11f2d721b973a1fbe8eaf45852305257362d6eebfb34b82ad734b`; seed 99681, seat 0, baseline rank 8, placements `[8,4,2,3,6,5,1,7]`, turns 13, decisions 40, completed, no truncation. Original downloaded bytes committed unchanged to `experiments/s-20261103-223b16589f/001-99681.json` and Git blob identity checked.
- No GitHub merge, no model version, no PPO steps, no model comparison. One genuine baseline game completed; no raw PPO games. Duplicate PR avoided: prior [#219](https://github.com/sstxww/reinforcement-learning/pull/219) already owns the same narrow fix, so [review handoff](https://github.com/sstxww/reinforcement-learning/pull/219#issuecomment-6586957449) was posted; task claim released and one-shot workflow retired.

## Acceptance and next action
This session's code and tests passed only in isolated Actions, not full PR CI. To minimize 10–20-session duplication, this branch remains an **unmerged supporting prototype**; do not open a PR for it. Review and integrate the already-open #219 after genuine original receipt, latest head CI and exclusive authorized merger. It cannot alone secure uncoordinated direct GitHub merge writes. PR #185 author must satisfy full evidence and actual global merge entry.
