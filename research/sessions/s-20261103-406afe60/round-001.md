# R001 — independent raw PPO action-selection ablation (V7)

**2026-11-03 UTC+8.** TASK_KEY `policy/raw-ppo-sampling-vs-argmax-99831`. Session `s-20261103-406afe60`, role EVALUATOR. Baseline main `3a745c6f6a48c65528bcbeb81b8627b8db93f046`.

## Inheritance and P0 review

Read complete V7 Gmail TXT (32,014 bytes). Inspected current main, PR #166 and #176, PR #15's non-main base / Draft #9 dependency, workflows, model registry, rank-eight prior issue #158. PR #176 was merged **by another session** during review. Exact main postmerge verification was still in progress, so not called successful. No lease, no main merge.

Historical 1408-step model source Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617 , expected SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Registry source hash `6d8712c93022ba11`, TavernGym 1.1.0, observe2 4017/447 and 245 legal-mask actions. **This is unpromoted**, not Best/Champion.

## Explicit testable hypothesis

A raw PPO distribution may put mass on multiple legal BUY action IDs while argmax repeatedly prefers a single FREEZE / REFRESH ID. Holding the exact original checkpoint, seed (99831), controlled seat (0), opponents (seven official bots), engine and mask fixed, compare single action choice from `model.predict(...deterministic=True)` to `model.predict(...deterministic=False)`. Both must have 0 fallback and 0 forced actions. The sampled policy is labeled sampled, **never misrepresented as deterministic argmax or new learned weights**.

The within-one-seed pair can expose a failure mode but cannot prove improved strength, isolate all confounders, or justify promotion.

## Implementation

- `tavern_ai/raw_sampling_probe_s406afe60.py`: public-observation hashes, legal mask validation, strict original model predict, per-turn 250-action bound; authentic eight-seat completed receipt only if `Game.is_over()`. Raw selection mode and sampled RNG seed recorded.
- `tests/test_raw_sampling_probe_s406afe60.py`: synthetic masked prediction tests, argmax/sampling flags, illegal actions fail without rescue.
- `.github/workflows/v7-raw-sampling-s-20261103-406afe60.yml`: single push-triggered bounded job, verified registered Release restore, baseline+argmax+sampled genuine matches, always-upload original evidence.
- Code/one-shot workflow commit `b7260914ab2d7264cc44f1abc41f63bdf7f598f3`.
- Actual workflow https://github.com/sstxww/reinforcement-learning/actions/runs/41511916662 launched; do not infer success from scheduling.

## Live data and budget

- PPO steps newly trained: **0**; 128-step continuation was already performed and found rank eight in merged PR #176; avoid duplicate low-signal spend.
- Seed 99831, 0 rotation, 1 per policy, planned receipts: `001-baseline-99831.json`, `002-argmax-99831.json`, `003-sampled-99831.json`. Not written until real Artifact is available.
- Mean placement/top-4 and BUY action rates: **unknown** until verified.
- Checkpoint/metadata: original Release read-only; no new weights, new Release, or durability claim. Champion/Best unchanged.
- PR/head-CI/merge/main-CI: pending; no exclusive integration lease.

## Next action

Read actual run 41511916662 and job log + Artifact; commit only genuine receipts. If sampled model loops, record the exact failure and compare with argmax as far as valid, without a fake rank; one substantive fix/test at most before retreating to a different hypothesis. After validated receipts, submit non-Draft isolated PR and request integrator review with exact SHA/head-run/remaining gates. Do not touch other session assets or main.
