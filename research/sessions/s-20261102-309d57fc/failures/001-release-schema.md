# V5 R001 failure loop — real V2 Release schema compatibility

## Failure signature and proof
- Actual isolated GitHub Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41428161019 (completed failure, SHA f4306604ddd162c197485c56419133819212c8af).
- Pinned TavernGym build and contract **passed**: engine 1.1.0, source hash 6d8712c93022ba11, features 4017, cards 447, actions 245, N_CARDS 3984.
- Genuine Release download command **succeeded**: `gh release download v2-learning-41413557445`.
- Exact failed call: `python -m tavern_ai.checkpoint_integrity checkpoints/source/model.zip --check-engine --expected-sha256 73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- Traceback: `ValueError: Unsupported checkpoint metadata schema` in the new verification module, **before** model load or training. No new steps, games or Release were produced by this run.

## Root cause
I initially implemented validator support for schema 1 only. The historical published learning models instead follow `tavern_ai/train.py` from unmerged PR #9, which emits **schema 2** and records `compatibility` containing engine, catalog_sha256, ruleset_id, patch_sha256, upstream_commit. This mismatch is in the new validation code, not proof the original ZIP is damaged.

## Corrective commits and tests
- `f8bb956`: accept schema 2 only when all above compatibility fields match pinned contract constants, in addition to ZIP integrity and SHA256 check.
- `fd632d2`: new models retain schema 2 and full compatibility fingerprint.
- `a4084d3`: unit regression validating genuine schema-2 layout and rejecting falsified catalog fingerprint.
- Local tests after code fix: **6 passed**. A real historical Release re-read + 128-step resume is still required to confirm the fix.
- New exact-head Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41428957815 (pending at documentation time).

## Limits and next gate
PR #92 remains Draft. Do not claim model recovery, resumed PPO or real match from either failed run; do not weaken `check_pr_evidence.py`. Only mark recovered after actual Release download, SHA verification, compatibility verification, Torch load, real 128-step continuation, model-controlled complete eight-seat match, CI success and publication of separate candidate artifacts. No Best/Champion promotion.
