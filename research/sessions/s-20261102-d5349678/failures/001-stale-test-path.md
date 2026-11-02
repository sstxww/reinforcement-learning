# Round 001 failure: stale PR source branch omitted main test file

- **Failure signature:** `ERROR: file or directory not found: tests/test_release_asset_verifier.py`; pytest exit code 4 during initial test collection, before TavernGym engine installation.
- **Actual GitHub run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41450357747 ; job `125293747755` failed, not a completed simulation; no game receipt to claim.
- **Source ref:** initial own workflow HEAD `4f8c07d28e826562f7d5b8d85543e34f7209762e`, branched from existing #93 head `650f62853a1ffc9a774e295e2959db929c127390`.
- **Reproduction:** run `python -m pytest -q tests/test_checkpoint_catalog_91b6e4a7.py tests/test_registry_integrity.py tests/test_release_asset_verifier.py` at that original SHA. The last test file is absent, although present in newer main; after `python -m tavern_ai.checkpoint_catalog` prints four historical candidates, pytest aborts on missing path.
- **Root cause:** integration workflow mixed a latest-main test path with an old historical PR tree; no evidence of a checkpoint/model bug.
- **Corrective action:** fast-forwardable two-parent merge of newer main `e1ef0f37497505f0f2902843af1bfdc15ebd198a` into own branch, preserving original #93 source and our isolated test fix; merge commit `638c0d4a1f3d20e95710bb504d8befd7346a6700`. Retry **once** after final documented workflow change; do not retry same failing SHA.
- **Final validation status at report creation:** not yet proven. Latest-head Python CI and actual pinned TavernGym full match still required.
