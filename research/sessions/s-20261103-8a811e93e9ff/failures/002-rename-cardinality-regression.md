# R001 CI failure — renamed-file cardinality regression after adding duplicate check

- **Session:** `s-20261103-8a811e93e9ff`; **TASK_KEY:** `security/trusted-ci-proof-paths`
- **Actual failed own workflow:** https://github.com/sstxww/reinforcement-learning/actions/runs/41515013072
- **Failing HEAD:** `6e16013f2aeb6a5e8c79bdf9bfcb25543facde32`
- **Job:** `125516235697`; step `Fail-closed trusted CI path regression tests` FAILED. Engine and eight-seat game steps were skipped; this failed attempt does **not** produce a completed new match receipt.
- **Actual failed tests:** `test_cannot_rename_away_trusted_validator` and `test_cannot_rename_over_trusted_workflow`. `pytest.raises(... match="trusted full-match")` received `Duplicate or missing PR file paths` instead.
- **Confirmed code cause:** `audit_changed_files` compared `len(changes)` (including both current filename and previous filename for a rename) against GitHub's `changed_files` (one entry per renamed file). This falsely interpreted a legitimate one-file rename as two changed files and masked the intended protected-file failure reason.
- **Minimal correction:** commit [43b50f4](https://github.com/sstxww/reinforcement-learning/commit/43b50f4cd7f7572e3c00f94f715ce8bfa4a9de95) counts **new/current filenames only** via `filenames`, while still keeping previous renamed paths in `changes` for protected-file audit. This preserves duplicate detection without hiding renamed trusted sources.
- **Retest:** a fresh own branch workflow and PR CI triggered by this real source change must be inspected at the new exact SHA. Do not count failed run #41515013072 as a success, and do not reuse the earlier source-head green run as proof.
- **Budget discipline:** this is the first code regression introduced during hardening; 1 meaningful fix, no request to rerun unchanged failed SHA and no PPO steps.
- **Evidence separate from failed branch run:** original independent TavernGym baseline completed in run [41513672032](https://github.com/sstxww/reinforcement-learning/actions/runs/41513672032), immutable original receipt SHA256 `ca47c459578a1949885edd6104f16dfa21cd09766cd65c672a08792e93fe607f`. Original game remains valid baseline-only evidence, not a new run/model claim.
