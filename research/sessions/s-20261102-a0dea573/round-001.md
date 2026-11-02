# V5 Round 001: registry promotion gate, integration first

Session: `s-20261102-a0dea573` | Base: `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`
Branch: `agent/s-20261102-a0dea573/optimization-001`

## P0 GitHub evidence (2026-11-02)
- At initial API read: 74 open PRs, 73 drafts, 15 model Releases.
- Only non-draft PR #15 targets `agent/learning/v1`; its prerequisite #9 is Draft. #15 HEAD `ad1bf93498ab5a310e0f4557dde1df7a97bf85fb` CI full-match succeeded, but no reviews and no improvement: V1/V2 paired ranks both [8,8,8,8]. Posted review blocking unsafe merger. No PR was eligible for immediate main merge from this reviewed subset.
- Latest main Release-indexed unpromoted PPO candidate: `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, 1408 cumulative steps. Registry reports pure candidate placement 8 on seed 99124 and heldout [8,8,8] on 99125–99127; baseline [6,8,8]; not a Champion.
- Existing `models/release_asset_digests.json` describes Release byte verification but not independent load and optimizer continuation from the published 1408-step tag. Do not state restore has passed from this Release.
- Latest stable `main` CI on `1afd8297e3c661bee3117ac5301b1ca08d64869b` passed before branch creation; main subsequently advanced, and fresh SHA must be rechecked.

## P1 narrow change
- Existing `tavern_ai.model_registry.read_registry` rejected an unverified Champion but accepted a synthetically verified label without independent hash/load/resume/full-match/gain evidence. Patch now requires all five explicit evidence flags before assigning Champion, retaining human audit as separate requirement.
- Validate `population`/`rejected` role references against immutable registered model IDs and duplicates.
- Add offline unit regressions. No policy weights, PPO hyperparameters, action masks, shared workflows or public canonical registry were changed.

## P2 behavior hypothesis (not yet a proven cause)
- Evidence supports rank-eight recurrence, but neither 1280 nor 1408 steps proves causal training insufficiency.
- Existing model probes distinguish legal BUY opportunities and policy-chosen END_TURN from guard-forced ends. A bounded real-game probe is proposed to measure actual raw action frequencies at an independent seed before any new training.

## Execution truth
- PPO training steps in this session: **0**.
- New true complete games: **2** (one Baseline, one unassisted published V5 PPO), independently executed in Actions #41450329264. Same seed 99231, both rank 8, baseline 60 decisions / model 122 decisions. Per-game authentic receipts committed at experiments/s-20261102-a0dea573/001-baseline-99231.json and 001-model-99231.json.
- Candidate promotion: **none**. No policy gain claimed.
- Release upload: **none**. Weights are not committed.
- Dedicated Actions #41450329264 finished success at workflow commit b33e97e5c05342ee61b3323ea31aedb83ce07e68. Artifact 13144398717 retrieved and inspected. Baseline and model completed; model 42 REFRESH / 70 FREEZE / 0 BUY across 38 BUY-legal exposures. Official Release SHA256 and one-action CPU inference validated; optimizer resume from published Release not run. Final HEAD PR CI still pending.

## Concurrent integration correction
- PR #138 (another session) independently implemented a stronger Champion evidence gate including unassisted games and fallback attribution. To avoid duplicate code/PRs, the Champion gate addition and duplicate tests on *this branch* were reverted. The retained unique code fix rejects stale/duplicated population and rejected model IDs. No modification was made to PR #138 or its branch.
- Initial isolated Actions run may reference the earlier commit with Champion changes. Its result must not be represented as CI on this branch's latest HEAD; a fresh PR CI is required once actual own-session game evidence is committed.

## Verified own-session cloud execution (post-initial snapshot)
- Workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41450329264 — **success**. It ran at commit b33e97e5c05342ee61b3323ea31aedb83ce07e68, before the latest branch documents and Champion deduplication.
- Artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41450329264/artifacts/13144398717 — downloaded and its three JSON documents plus preflight log inspected.
- Seed 99231 original baseline: place 8, 14 turns, 60 decisions, complete, true game; source receipt experiments/s-20261102-a0dea573/001-baseline-99231.json.
- Same seed original V5 model: place 8, 15 turns, 122 decisions, complete, *unassisted*, true game; source receipt experiments/s-20261102-a0dea573/001-model-99231.json.
- Model weights SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632; Release bytes downloaded and verified; archive passed preflight, actual CPU-load and single public action inference passed. The published Release's optimizer continuation **has not been validated in this session**, and no new weights were created.
- Pure model chose REFRESH 42, FREEZE 70, BUY 0 despite 38 BUY-mask-legal decision exposures. Model/Baseline same seed both rank8; no strength claim. Permanent distilled report reports/s-20261102-a0dea573/001-published-v5-raw-99231.json.
- The initial dedicated Action passed its own tests, but the current branch HEAD has evolved: require fresh exact-head PR CI before merge. No direct main write.

## Handoff
Only after the independent workflow and actual receipt exist should this PR be considered for integration. Never synthesize a canary receipt; if workflow is blocked, leave Draft and record the run error. Audit the branch's actual head and main CI before merge.
