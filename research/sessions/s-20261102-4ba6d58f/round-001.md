# s-20261102-4ba6d58f — Round 001: P0 audit, P1 model storage index

## P0 — verified existing integrations
- Started with V5 Gmail attachment; reviewed main, 66 open PRs, six Release models, CI, training and evaluation code.
- PR #47 had already joined main for seat-aware evaluation.
- PR #25 strict receipt audit merged concurrently at f29a0a6e99161aca4163e51427f6bfabbe02f76f; do not claim this as own merge. Subsequent PR #70 pinned mechanics audit also merged concurrently into 3c65ffd0380d6269e6b39c7bf1ca2d84281546d8.
- Do not merge PR #15 before its dependency #9; reported V2 model skill gain is zero and #15 is not a Champion candidate.
- Unmerged PRs overwhelmingly Draft/negative pilots; avoid forced merge, duplicate instrumentation and accidental branch overwrite.

## P1 — precise checkpoint claims
- Main shared train.yml currently restores a 90-day Artifact; existing Release weight files are durable indexed assets, not yet verified resumable models.
- Added six Release indexes with expected model/metadata SHA256, preserving model lineage where available and marking every actual download/load/resume/full game check false.
- Added a safe offline verifier (streaming SHA256; pinned 1.1.0 engine + 4017/447/245 contract; strict lineage/Champion/Latest checks), optional SB3 load flag and regression tests. It does not change trainer or release assets.
- Local pure Python tests: 13 passed; synthetic weights were only fixtures, not trained models.
- An isolated bounded workflow runs the registry tests, verifies pinned TavernGym and plays one REAL eight-seat baseline engineering canary seed 49123; workflow result and receipt pending actual execution, with no fake metrics.

## P2 — ranked-eighth evidence is still causal-hypothesis level
- Existing PR #15: resumed V1 256 steps to V2 1280, four heldout old/new ranks [8,8,8,8] each, baseline [7,6,8,8]. No observed improvement.
- Existing PR #60: low-LR PPO candidate reportedly made 0 purchases over 3 full games, reference made 20 and showed 40 repeated identical actions. Sample only three; distinguish no-buy choice from absence of legal buys before claiming root cause.
- Priority next is legal-opportunity conditioned BUY/PLAY/END_TURN telemetry, economy per turn, fallback counts and unbiased seat-aware paired tests. Do not increase PPO budget before recovery and diagnostics.

## Handoff
- Branch base: 3c65ffd0380d6269e6b39c7bf1ca2d84281546d8.
- This session trained 0 PPO steps; completed 0 new model matches; no Champion.
- Receipt and exact CI URLs must be appended only when actual executions return success. No direct main push or Arena ranked execution.
