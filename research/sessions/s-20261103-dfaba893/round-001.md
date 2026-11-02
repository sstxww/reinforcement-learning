# V7 R001 — PR #175 safe checkpoint rollback counterexample

## SYNC / TRIAGE
Read complete V7 email TXT (32,014 bytes), canonical AGENTS and protocol, current main `c1b828734527bae6141805581693d890cc3bff94`, in-flight PRs #175/#185, live CI. The main 41512315964 pipeline has since finished SUCCESS. No global main merge lock was acquired; branch protection metadata indicated main was unprotected, and PR #185's proposed workflow explicitly does not exclude direct out-of-band merge calls.

## Falsifiable claim and reproduction
The PR #175 helper uses `if destination.samefile(source): destination.unlink()` after an exception on installing a second hardlink. Even when all `os.link` creations are exclusive, a legacy concurrent writer can rename-replace the first destination **between those two calls**. Python's `samefile` confirms the inode *at a past instant*, not a compare-and-delete operation. The following schedule is deterministic:

1. Our verified staged ZIP is linked at destination.
2. Rollback checks inode identity: True.
3. Concurrent writer replaces that destination with its own checkpoint.
4. Rollback unlinks the path, deleting the concurrent writer's checkpoint.

Run `python reports/s-20261103-dfaba893/rollback-toctou-reproducer.py`. This is a **synthetic counterexample** to the primitive, not an invocation of the actual PR #175 production function. Local result: `other_writer_checkpoint_deleted: true`, source staged weights preserved. The test in #175 replaces the destination **before** `samefile` and cannot exercise this ordering.

## Provenance and remaining gate
GitHub review comment actually posted: https://github.com/sstxww/reinforcement-learning/pull/175#issuecomment-6586804588 . PR #175 originally advertised exact-head full-match CI success https://github.com/sstxww/reinforcement-learning/actions/runs/41511418837 (baseline infrastructure only), but its older base `70c411b64034c8f66618811ff7a98914395735a5` is behind main. This review is **not** author approval, independent gameplay, model evidence, or a main merge.

## Outcome and next test
No changes to PR #175's production file, other sessions' branches/models, main, or Champion. Work stays isolated. Owner should add a test that injects replacement **after** the positive identity check, and choose fail-closed handling without pretending that pathname comparison plus unlink is atomic. If an implementation is patched, verify on actual merged code; do not classify synthetic review as fix success.

Training: +0 steps. Actual raw-model games: 0. New Releases: 0. No claim of policy strength. Limited read-only pinned-engine baseline workflow is configured separately and must be verified from Actions original receipt.
