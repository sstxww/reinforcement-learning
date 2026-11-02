# V7 session s-20261103-d8bde8c1

- TASK_KEY: `ci/merge-base-bound-run-regression`; ROUND: 001; ROLE: P0 REPAIRER / REVIEWER; status: running / CI and genuine game pending.
- BASE_MAIN_SHA at branch creation: `c1b828734527bae6141805581693d890cc3bff94`; HEAD: see branch history; work branch: `agent/s-20261103-d8bde8c1/optimization-001`.
- Atomic task claim: `claims/v7/ci-run-exact-merge-base-evidence` (task only, NOT a merge lease). Never interpret as permission to write main.
- Read V7 full 32,014-byte Gmail TXT. Prior work examined: Issue #182 (CAS lease does not stop out-of-band mergers), PR #185 (serial integration gate), PR #175 (durable Release restore no-clobber), PR #184 (PR readiness audit), PR #186 (assisted receipt).
- Source finding: original successful PR #175 CI #41511418837 was HEAD `8f4be75cba8463a3f0a74f0e0b72a027a0bad8b5`, bound base `70c411b64034c8f66618811ff7a98914395735a5`; inspected current main was `c1b828734527bae6141805581693d890cc3bff94`. Therefore original success is NOT a merge-code check for this latest main.
- PR #185 review posted: https://github.com/sstxww/reinforcement-learning/pull/185#issuecomment-6586826368 ; requested exact `run.pull_requests[].base.sha` gate instead of timestamps.
- Independent addition: offline fail-closed helper `scripts/v7_ci_merge_base_d8bde8c1.py`, 15 synthetic regressions, bounded read-only workflow and genuine baseline-only game plan (seed 99679).
- Source/model facts: registered latest unpromoted V5 1408 steps, Release https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; TavernGym 1.1.0, observe2 4017/447/245. Release/optimizer NOT downloaded/revalidated by this session.
- New PPO steps: **0**; own newly persisted checkpoint/Release: **none**; complete own TavernGym game: **pending Actions**; raw PPO games **0**; promotion **none** (best/champion not changed).
- Own merges: **none**. Latest exact-head PR CI and game proof to be recorded only after real results. Main currently unprotected; no global exclusive integration lock demonstrated.
- Next operation: check own workflow run, obtain original actual eight-seat baseline receipt from successful run (do not fabricate), commit it to `experiments/s-20261103-d8bde8c1/001-99679.json`; check independent PR CI; ask gate author to integrate exact-base regression, then recheck freshest main SHA and CI. Do not merge without mandatory review and truly exclusive entry.

## Actual GitHub submission and handoff
- Submitted **non-Draft** PR https://github.com/sstxww/reinforcement-learning/pull/218 from implementation commit `3be8071619706bbc53c224d7cd18b134d3ea9a4d`. PR head may advance with this handoff update; re-fetch for exact head before any gate.
- Genuine baseline workflow https://github.com/sstxww/reinforcement-learning/actions/runs/41513547274 — **queued, outcome unknown** at last observation. Do not make or commit a completed-game receipt until an original artifact or log proves real successful eight-seat completion.
- PR CI https://github.com/sstxww/reinforcement-learning/actions/runs/41513849788 — **queued, outcome unknown** at last observation; current submission lacks own validated session receipt, so should not be merged.
- Independent review comments: PR #185 https://github.com/sstxww/reinforcement-learning/pull/185#issuecomment-6586826368 ; PR #175 https://github.com/sstxww/reinforcement-learning/pull/175#issuecomment-6586907143 ; Issue #182 https://github.com/sstxww/reinforcement-learning/issues/182#issuecomment-6586908072.
- Next exact action: check run **41513547274**, inspect job steps & original Artifact, commit verified actual receipt to `experiments/s-20261103-d8bde8c1/001-99679.json`; then verify new PR #218 HEAD CI. If run fails, log the first real error and fix with bounded rerun; if queued, do not call it failed or successful.
- State: **blocked_on_external_Actions_queue**, no merge lease or verified model/game improvement. Task claim released/handed off after this submission; another agent may pick up #218.
