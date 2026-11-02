# s-20261102-847b6d4e R001 — P0/P1 strict Release verification integration

## Ownership and baseline
- Session: s-20261102-847b6d4e; branch `agent/s-20261102-847b6d4e/optimization-001`; parent main HEAD at creation: `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
- Scope: integrate two **already merged** main validators, not create a second registry or copy PR #93's stale candidate count.
- Current main began with 75 open PRs, 74 draft; no non-draft independent safe merge target (PR #15 is stacked on draft #9).
- PR #93 is draft and has a hardcoded four-candidate test while main registry already has five; it also overlaps the already merged Release verifier. Therefore **not merged** and not modified.

## Actual patch
- Compose `tavern_ai.release_asset_verifier.verify_local` with `tavern_ai.checkpoint_preflight.audit_archive`.
- A pair of matching SHA256 digests is no longer sufficient to report safe local verification: validate strict PPO ZIP CRC, required `policy.optimizer.pth`, bounded archive, and checkpoint metadata schema-2 full compatibility too.
- Tests use **synthetic** valid ZIP fixtures only and new negative cases with matching expected digests for non-ZIP, missing optimizer and invalid schema. They are regression evidence, **not** model artifacts.
- No change to weight bytes, trainer, evaluator, policy, Champion/Best or shared main train workflow; zero PPO steps.

## Real-game and CI status
- Own branch-scoped pinned TavernGym 1.1.0 baseline eight-seat canary: seed **84761**.
- Honest pending gate: the receipt exists **only if** dedicated GitHub Actions run completes and commits `experiments/s-20261102-847b6d4e/001-84761.json`; it must pass `tavern_ai.validate_receipt`.
- The PR's separate latest-head CI and main CI after an eventual merge must both succeed. No merge or success is claimed ahead of actual checks.
- No model-only game or Release re-download performed in this session. Main's latest 1408-step candidate is unpromoted and remains eighth in its recorded evaluation.

## Next
1. Verify own canary, latest PR CI, exact SHA and main compatibility.
2. Have integrator review this extraction in preference to merging duplicate PR #93 verbatim; coordinate before closing the original.
3. Only then consider a safe PR merge and confirm post-merge main CI; keep diagnosing action loops before large PPO runs.
