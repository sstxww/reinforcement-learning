# V7 R001 — Release CPU load is not masked TavernGym inference

SESSION_ID: `s-20261103-4eba9fda`; TASK_KEY: `p1/release-masked-inference-gate`; BASE_MAIN_SHA: `c1b828734527bae6141805581693d890cc3bff94`.

## Historical reuse

Main train.yml already performs fail-closed GitHub Release checkpoint restore (#117), SHA-bound optimizer resume (#161), schema-2 metadata preservation (#164), and separate publisher credentials (#165). Registry Latest remains a 1408-step **unpromoted** experimental model, not Champion. A separate rejected 1536-step model documented Play/Cancel loops and failed full games, so **do not blindly extend PPO steps**. Existing PRs #174/#179 are independently ready for review; none grants this session a main merge lease.

## Actual defect and minimal repair

Before the change `release_asset_verifier.verify_local(..., check_load=True)` called `MaskablePPO.load(..., device='cpu')`, checked historical step counts, set `sb3_load_checked=True`, and returned. It did not create an environment, compute a legal mask, call `predict`, or step the engine; the train restore Action labelled this as CPU inference. The new `_probe_masked_inference` uses pinned `TavernEnv(seed=7819)`, checks 245 mask entries and at least one legal action, passes the real mask to deterministic model.predict, rejects out-of-range or masked-illegal actions, makes one actual environment step, closes env in `finally`, and reports a separate explicit `masked_legal_inference_checked` boolean. A failed inference raises, so restore aborts before installing the model. One-step inference is not a completed game or optimizer continuation.

Offline regression tests are synthetic only: legal prediction, illegal masked prediction, out-of-range action, missing/empty mask, environment cleanup, verify_local success flag, fail-closed integration, and skip-load no-credit. No synthetic test or fixture counts as a completed eight-seat match.

## Execution / budget / evidence

One bounded branch-only Github Actions job, Python 3.12, tests, verified TavernGym 1.1.0, canonical Release restore with actual SHA-checked checkpoint, one masked inference, and one independent baseline-controlled authentic eight-seat match seed 99657. This is an infrastructure match, **not** a candidate model performance test. Runtime/action/results pending until job truly completes. No arbitrary bulk PPO/rejected model training. No credentials in branch.

- Additional PPO steps: 0, no new checkpoint metadata/hash, no optimizer state advanced, no new Release, no Best/Champion.
- Heldout paired rank delta: not measured in this session (n=0). Historic 1408-step model heldout [8,8,8] versus baseline [6,8,8] is inherited historical data, not our own result.
- Empirical root cause of rank8: **unknown**; masked-inference integrity gate is an engineering correctness fix, not a strength fix.
- Failure signatures and logs: will be captured if Actions fails; limit retries to a meaningful change rather than repeat identical runs.

## Integration preconditions

Require current PR head CI and true eight-seat receipt, code review (particularly whether installed registered V5 checkpoint can produce legal masked predictions), no overlap with current main, exclusive serialization lock, and then main-head Actions success. No main push or forced merge.

## Verified real execution 2026-11-02T19:51 UTC
- [Own original Actions #41513145899](https://github.com/sstxww/reinforcement-learning/actions/runs/41513145899) completed SUCCESS: 29 regression tests, TavernGym 1.1.0 native patched engine check, registered V5 1408-step Release download with SHA/metadata verification and masked legal model inference, plus a separate authentic full baseline-controlled eight-seat match.
- Original saved game receipt: `experiments/s-20261103-4eba9fda/001-99657.json` directly extracted from [Artifact 13174935836](https://github.com/sstxww/reinforcement-learning/actions/runs/41513145899/artifacts/13174935836). Seed 99657, raw **baseline** (not PPO), controlled seat 0 rank 8, full permutation [8,5,2,7,1,6,3,4], turns 15, decisions 47, completed true, zero truncated combat, no turn limit end.
- Original verified registered Release report: `reports/s-20261103-4eba9fda/001-verified-release-restore.json` SHA256 82f7c15257538f27213291a29321e1eae50e8b56f53d72219f0f8ee4e5f5add3: 1408 steps, weights+metadata SHA verified, CPU load and legal masked inference real call succeeded on pinned engine. This is not optimizer continuation or full-game raw PPO performance: **new training steps 0**.
- The succeeded one-shot workflow was deliberately retired after the run (commit `cd8fcb83213ad9d0bd0ed153fd6c50cac2321496`), but its original commit `9d8c40bfdc9a3032bdba05fe183ffc3ae0f761df`, runner logs, artifact and immutable URL remain available.
- These checks resolve the *specific inference-integrity gap* for this source branch only. Next require independent exact-head PR CI on current base/main and review by a serialized integrator. The registered model still has no demonstrated competition improvement and Best/Champion stays null.
