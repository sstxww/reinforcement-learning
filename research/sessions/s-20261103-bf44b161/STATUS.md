# V5 s-20261103-bf44b161 — integration status (round 001)

- Status: `integration_patch_submitted_for_validation`; no Champion promotion and **no new PPO training**.
- Base main at branch creation: `185a5fd80114e09789dd080d2edabdf88279a9cf`.
- Branch: `agent/s-20261103-bf44b161/optimization-001`.
- Scope: fail-closed restoration of the existing main-only `.github/workflows/train.yml` without altering model weights, canonical evaluation, model registry, Arena or any other session.
- Own code: `scripts/restore_checkpoint_fail_closed.sh`; `tests/test_restore_checkpoint_fail_closed.py`; isolated bounded proof workflow `.github/workflows/v5-proof-s-20261103-bf44b161.yml`.
- Independent proof seed: `98631`. Original complete eight-player baseline receipt expected at `experiments/s-20261103-bf44b161/001-98631.json` **only if the job actually completes**. Not yet claimed.
- Main PR audit: 115 open PRs / 114 Draft as of audit; sole non-Draft #15 depends on #9, so no unsafe merge. Recent already-merged #120/#153/#152 are **other agents' merges**, not this session's work.
- Existing canonical latest experimental PPO: 1408 steps, Release `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; Best/Champion unassigned. No new model archived by this session.
- Prior strong diagnosis: seed 99128 main report showed 35 legal BUY decision states / zero BUY for model, 37 rerolls, 70 other actions, rank 8; the same-seed baseline bought 14/21 and also rank 8. Draft #107 reports 46 forced buys without rank benefit. These are **observations and unverified causal hypotheses**.
- P0/P1 blocker: shared train.yml previously silently restarted PPO from random weights when expired/failed Artifact was unavailable. This branch removes that fallback. More work is required for durable Release fallback and trusted archive SHA256 preflight. 90-day Artifact is NOT durable; no claim of full production continuity.
- Additional control: CI full-game baseline match is only **infrastructure evidence**, not raw PPO proof or strength improvement. Do not launch large PPO or ranked Arena from this PR.
- A live integration audit and blockers were saved in [Issue #3](https://github.com/sstxww/reinforcement-learning/issues/3#issuecomment-6586013449).
- Next validation: check exact head GitHub Actions CI, independently verify own receipt and pinned engine, review current main for conflicts, and integrate only after code-owner review. Selectively reconcile overlapping #121/#147/#149 rather than merge all.
