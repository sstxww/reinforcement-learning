# AutoTavern V7 isolated raw-model evaluation — s-20261103-ff75e61a

- **TASK_KEY:** `eval/raw-v5-1408-paired-seed-99541`; **ROUND:** 001; **ROLE:** EVALUATOR / P0 independent reviewer; **state:** claimed.
- **Atomic task claim:** `claims/v7/eval-v5-1408-seed-99541`, owner record commit `bc4844cb713e9b02dc8e9289595a4b932d3fdfa9`.
- **BASE_MAIN_SHA:** `c1b828734527bae6141805581693d890cc3bff94`.
- **Branch:** `agent/s-20261103-ff75e61a/optimization-001`; commit SHA and PR will be updated after actual run.
- **Scope:** read-only source main and existing published **V5 1408-step** PPO; paired same-seed full eight-player match with `policy=model` **without guard or baseline substitution**, plus an independently executed baseline at seed **99541**, controlled seat **0**, TavernGym **1.1.0** / source hash `6d8712c93022ba11`.
- **Model ID / Release:** `v5-s-20261102-68099929-1408-41428692617`; [immutable versioned source](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617), checkpoint SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- **Model steps in this session:** 0 planned (investigate unassisted performance first); no optimizer restore, new weights or Release claims. Best/Champion on main are null.
- **Isolation:** shared `train.yml`, evaluation module, weights/registry, existing PR branches and Release assets are not modified.
- **Work reused:** main's `tavern_ai.canary`, `tavern_ai.validate_receipt`, `tavern_ai.paired_receipt_gate_v5`, CI. Historical PR #168 same-seed 99385 baseline rank 7 vs raw 1408 rank 8; independent seed is needed.
- **Concurrent P0 review:** [PR #185](https://github.com/sstxww/reinforcement-learning/pull/185) HEAD `a07bd90d2ce886f9cdf54263ed44b81a2d28b212` has failed [CI #41512690022](https://github.com/sstxww/reinforcement-learning/actions/runs/41512690022) for missing own receipt after 390 passing tests. Submitted independent [review 5742385698](https://github.com/sstxww/reinforcement-learning/pull/185#pullrequestreview-5742385698) documenting stale-created-CI-rerun risk; reviewer is NOT main integrator.
- **Main integration lease:** none; no merge authority, zero merged PRs.
- **Run status:** branch-only bounded workflow will be the authoritative source; no game is claimed completed before genuine run/job and original receipt is read.
- **Next:** create isolated workflow, inspect real Action, persist original model/baseline receipts or a distinct failure diagnostic; run strict receipt compare if raw succeeds; update handoff and exact-head CI.


## Verified R001 completion — genuine original GitHub proof (2026-11-02 19:54 UTC)

- **State:** executed and evidence verified; final PR / exact latest-HEAD CI are the remaining review gates. No main merge or main-exclusive lease.
- **Main checked immediately after run:** `c1b828734527bae6141805581693d890cc3bff94`, exact-main [CI #41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964) SUCCESS. This is **pre-merge main**, not a new post-merge test.
- **Round execution commit:** `d4c3d7f6dab880e275c2195879713444f500c93b`, [real run 41513501276](https://github.com/sstxww/reinforcement-learning/actions/runs/41513501276) **SUCCESS**, job `125511026704`. Own isolated tests, pinned-engine bootstrapping, baseline game, immutable Release download SHA check, raw-model game, paired report and Artifact all succeeded.
- **Original Artifact:** [13174107805](https://github.com/sstxww/reinforcement-learning/actions/runs/41513501276/artifacts/13174107805). Original raw `experiments/s-20261103-ff75e61a/001-99541-raw-model.json` and baseline `experiments/s-20261103-ff75e61a/001-99541-baseline.json`, plus `reports/s-20261103-ff75e61a/001-99541-paired.json`, are committed *byte-identical* to downloaded original ZIP; all three git blob SHA values matched original raw bytes independently.
- **Raw PPO:** existing registered 1408-step V5 Release weight SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, seed **99541**, seat 0, policy model (no guard/baseline fallback), true complete TavernGym 1.1.0 8-seat game, rank **8**, 15 turns, 123 actions, ranks `[8,2,6,1,7,5,3,4]`, `truncated_combats=0`, `turn_limit_end=false`. Original receipt SHA256 `dc6894052e31aa004c231f47ea7774822e83ccac644ea435d7dfb019b983250a`.
- **Independent baseline:** same seed/seat/opponents, rank **8**, 14 turns, 38 actions, ranks `[8,2,4,6,5,7,1,3]`, complete and no truncation. Original receipt SHA256 `ca63ecd3a223c11f4c8acdeba3665499bc38ab30518abe5c15049d56e8b4092e`.
- **Paired n=1:** delta 0.0, both top4 0.0, no CI because insufficient pairs; original paired report SHA256 `fd8113104efb0a46bc2224613cfc45240f7af85aa7beac152c1275f48732d401`. No global strength equality inference; no model promotion.
- **New PPO training:** exactly **0** steps this session, 0 new checkpoints, 0 optimizer-resume executions, 0 new model Releases; source model was loaded after Release SHA check. Best/Champion unchanged at null. Training/optimizer persistence NOT retested here.
- **Reviewed other PRs:** #185 (real first PR head CI `41512690022` failed missing receipt, 390 passed), independent code-review comment [#185 review 5742385698](https://github.com/sstxww/reinforcement-learning/pull/185#pullrequestreview-5742385698) describes possible stale original CI rerun gate. No other PR branches changed.
- **Hypotheses:** no attributable rank-eight root-cause demonstrated; specific new same-seed observation PPO/baseline both rank8. Do not claim action-level BUY counts from this uninstrumented raw canary.
- **Failures:** none in our own run; review of #185's failed head CI is external and that agent must perform its own receipt/CI fix. No blind retry initiated.
- **Integration:** no merge. Exclusive main integration not established; current V7 proposed serial workflow is cooperative only and not enforced universally. PR exact-head CI and independent review pending; do not use direct REST merge.
- **Next concrete handoff:** inspect the PR for this branch, its exact HEAD SHA and fresh `CI - full-match gate` success including actual full-match step and original receipts; separately confirm a truly exclusive main merge gateway before attempting squash merge expected-head SHA; then verify actual postmerge main CI. For model research, isolate raw BUY mask/loop causal instrumentation on a NEW predeclared seed/seat without modifying this immutable receipt.

## Submitted non-Draft PR for independent integration review

- [PR #231](https://github.com/sstxww/reinforcement-learning/pull/231) created **open, non-Draft**, base main `c1b828734527bae6141805581693d890cc3bff94`, initial proposed head `b59750ca5caecc7afc55b23fefa8a573ec27f21f` (before this status append). The PR is **not merged** and there is no exclusive integration lease. Do not treat prior raw workflow success as latest PR CI.
- The final expected HEAD is this status-update commit, query GitHub PR HEAD immediately before review/merge; perform latest exact-head PR CI. This avoids recording a fabricated self-referential commit SHA.
- Original real model/baseline files and paired report are already byte-verified and saved, so independent PR gate `scripts/check_pr_evidence.py` can now check real receipt and separate simulator CI.
- PR independent approval, current-main compatibility and global main exclusivity remain gating conditions. No other agents' changes or models were overwritten.
