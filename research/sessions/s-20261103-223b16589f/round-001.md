# R001 — CI workflow source trust boundary

## Existing work and precise hypothesis
Read V7 TXT (32,014 bytes), main CI #41512315964 and PR #185 source code/CI logs. Its `check_run` and `check_jobs` use workflow path, job/step names and conclusions to infer that tests/engine/real game executed. A PR might alter its own CI workflow while preserving the same public names. **Hypothesis, not an observed malicious attack**: success by step-name alone is insufficient for trust. The independent gate should detect edits to the trusted workflow/critical scripts on both renamed-from and renamed-to paths.

## Implementation
Own only `scripts/v7_ci_definition_guard_223b16589f.py`, `tests/test_v7_ci_definition_guard_223b16589f.py`, session-specific one-shot workflow and session evidence. Read-only GitHub REST retrieval with exact main/head SHA, two identity checks, full changed-file pagination and a deliberately conservative CI trust-boundary denylist. Test rename, tampered CI, duplicate/malformed paths, pagination, concurrent head/main change. Expose no merge writes and no tokens in logs.

## Original evidence and budget
- Main@start `c1b828734527bae6141805581693d890cc3bff94`; CI #41512315964 SUCCESS.
- PR #185: HEAD `a07bd90d2ce886f9cdf54263ed44b81a2d28b212`, CI #41512690022 failed at *Missing independent agent game receipt*, after 390 passed/1 skipped. Parent game run #41512683244 was queued on inspection.
- Task claim `claims/v7/ci-workflow-integrity` creation succeeded atomically; it is **not** a global merge lease.
- Own workflow: smoke budget one baseline eight-seat seed `99681` with TavernGym 1.1.0, separate from model; limited timeout; no model training.
- No GitHub merge, no model version, no PPO steps, no model comparison; game receipt pending actual workflow result.

## Acceptance and next action
Run isolated regression + pinned engine contract + actual baseline eight-seat game in Actions; extract original receipt, validate and commit unchanged; submit non-Draft PR and verify exact head shared CI. This guard must be integrated selectively with #185; it cannot alone secure uncoordinated direct GitHub merge writes. PR #185 author must fix its own missing receipt, obtain valid independent approval and enforce one actual merge entry.
