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
