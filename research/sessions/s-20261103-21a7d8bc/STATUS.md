# AutoTavern-AI V7 — s-20261103-21a7d8bc handoff (R001)

- STATUS: ready_for_integration_review; original experiment and Release complete; new PR head requires exact latest-head CI; no exclusive main merge lease.
- TASK_KEY: eval/v7-raw-buy-replication-97421
- ROLE: EVALUATOR / REPAIRER, **not** exclusive INTEGRATOR
- TASK CLAIM: `claims/v7/raw-buy-replication-97421` (created by this session; no main integration lock)
- BRANCH: `agent/s-20261103-21a7d8bc/optimization-001`
- ORIGINAL_MAIN_BASE: `3a745c6f6a48c65528bcbeb81b8627b8db93f046`; main advanced concurrently to `c1b828734527bae6141805581693d890cc3bff94` on last check
- OWN TRAINING+REAL-GAME RUN: https://github.com/sstxww/reinforcement-learning/actions/runs/41512015082 **SUCCESS**; all test, pinned engine, trusted Release, match, train, candidate and upload steps green
- ORIGINAL RECEIPT ARCHIVER: https://github.com/sstxww/reinforcement-learning/actions/runs/41513677139 **SUCCESS**; commit `8af5721734c765778916fdd8b63021c7a7d00374` copied exact authenticated original receipts and model metadata
- ARCHIVE FIRST FAILURE: https://github.com/sstxww/reinforcement-learning/actions/runs/41513467624 (no jobs, invalid job-level runner context); minimal fix commit `2fa7624aee6648f4d49a9b50e3d4df7b76fb51f3`, verified next run green
- ORIGINAL BASELINE: `experiments/s-20261103-21a7d8bc/001-baseline-97421.json`; seed 97421, seat 0, completed, rank 7, decisions 44, BUY 13 / 23 masked legal opportunities
- ORIGINAL RAW PARENT: `experiments/s-20261103-21a7d8bc/002-raw-1408-97421.json`; seed 97421, seat 0, completed, rank 8, decisions 126, BUY 0 / 43 legal, REROLL 45, FREEZE 70
- ORIGINAL CANDIDATE: `experiments/s-20261103-21a7d8bc/003-candidate-97422.json`; seed 97422, seat 0, raw candidate completed, rank 8, decisions 124, no fallback or guard, all three games no combat truncation
- PAIRED DESCRIPTIVE AUDIT: `reports/s-20261103-21a7d8bc/001-matched-buy-97421.json`; one matched seed, n=1, raw rank one worse than baseline; no uncertainty or strength claim from one match
- ENGINE: pinned TavernGym 1.1.0 / source `6d8712c93022ba11`, observe2 4017 floats + 447 card indices, 245 masked actions
- PARENT 1408-step RELEASE: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617; SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`
- ACTUAL PPO RESUME: 1408→1536 (`+128`), seed 97421; candidate SHA256 `cf34d9728dc50d97707c2c65c6095f330c84c07d0763963db675484f2d797d7c`; explicit CPU load and optimizer state provenance verified
- CANDIDATE MODEL STATUS: `models/sessions/s-20261103-21a7d8bc/candidate-1536.status.json`; unpromoted/rejected for rank8, Best/Champion unchanged
- MODEL WEIGHT STORAGE: **durable experimental unpromoted prerelease** https://github.com/sstxww/reinforcement-learning/releases/tag/v7-s-20261103-21a7d8bc-1536-41512015082; 17,525,202-byte candidate model.zip SHA256 `cf34d9728dc50d97707c2c65c6095f330c84c07d0763963db675484f2d797d7c`, independently re-downloaded and SHA-verified by https://github.com/sstxww/reinforcement-learning/actions/runs/41515765298 **SUCCESS**. Original source Artifact still expires 2026-11-16; Release does not. No Best/Champion, no improvement claim.
- TEST: 8 synthetic negative/positive proof assertions in `tests/test_v7_buy_pair_s_20261103_21a7d8bc.py`, actual Actions test step passed; synthetic tests are NOT game evidence
- REUSED MERGED: PR #176 FREEZE taxonomy + real resume; PR #165 least-privilege Release publisher; did not edit shared `train.yml` or main
- PR: https://github.com/sstxww/reinforcement-learning/pull/232, non-Draft, 14 isolated files. Exact previous head `0475af195989a491b9f00ef2bd8404b9fc678088` PR CI https://github.com/sstxww/reinforcement-learning/actions/runs/41515008682 **SUCCESS**, including new complete 8-seat baseline match. **This manifest update changes PR HEAD; reverify latest-head CI after update.**
- MAIN INTEGRATION: NOT performed; task claim is NOT an exclusive main integration lease. `coord/autotavern-main-integrate:coordination/merge_lease.json` recorded a prior merge during lease ownership; no global-enforcement proof. Release publisher also did NOT write main. Review PR diff, exact-head CI, main SHA and branch conflicts before any merge
- NEXT ACTION FOR NEXT SESSION: fetch this branch and PR; check exact PR HEAD `CI - full-match gate`, read `experiments/s-20261103-21a7d8bc/002-raw-1408-97421.json` and original Action #41512015082; only then initiate a *new, separately claimed*, fixed-seed Freeze/no-progress/BUY-logit probe. Do NOT simply force BUY or promote 1536 candidate.

## R002 durable model custody (separate owned branch)

- TASK_KEY: `archive/v7-rejected-1536-s-20261103-21a7d8bc`; claim `claims/v7/archive-1536-s-20261103-21a7d8bc`; branch `agent/s-20261103-21a7d8bc/optimization-002`.
- Source original training run #41512015082 and verified archiver #41513677139.
- Model Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v7-s-20261103-21a7d8bc-1536-41512015082. Publish + independent re-download SHA run #41515765298 **SUCCESS**; seven assets (model.zip, metadata, three full-game receipts, paired report, sha256sums.txt). This is **not** model promotion and no registry changes.
- On a subsequent unrelated new model experiment, use fresh task claim and heldout seeds; do not continue training based solely on rank 8 candidate.
