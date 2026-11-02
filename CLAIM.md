# V7 atomic task claim — p0/v7-main-integration-entry

- Claim ref: `refs/heads/claims/p0-v7-main-integration-entry-001`; created successfully (exclusive creation of this ref, not exclusive main merge lease).
- Owner: `s-20261103-0a1a530f32`; Round: 001; Created on 2026-11-03 project local date; base main: `c1b828734527bae6141805581693d890cc3bff94`.
- State: `handoff_pending_latest_head_ci` (active code branch but no main merge privilege).
- TASK_KEY: `p0/v7-main-integration-entry`.
- Work branch: `agent/s-20261103-0a1a530f32/optimization-001`; proposed PR: https://github.com/sstxww/reinforcement-learning/pull/205.
- Owned files only: `scripts/v7_merge_safety_0a1a530f32.py`, `tests/test_v7_merge_safety_0a1a530f32.py`, `research/sessions/s-20261103-0a1a530f32/*`, `research/knowledge/proposals/s-20261103-0a1a530f32-001.md`, `experiments/s-20261103-0a1a530f32/*`.
- Evidence run: https://github.com/sstxww/reinforcement-learning/actions/runs/41513118163 (success; seven regression cases and complete baseline full game). Exact-head CI: https://github.com/sstxww/reinforcement-learning/actions/runs/41513964846 (queued at claim-note creation).
- Completion condition: own PR receives latest-head CI and review handoff, and task claim is explicitly marked released. **Never infer global integration exclusivity** from this claim.
- No lease over `coord/autotavern-main-integrate`; no other writer must wait for this claim to merge its independently reviewed work if a real server-enforced gate exists. However Issue #182 confirms such a gate was not proven as of inspection.
- Recovery: if the owner conversation stops, treat this claim as a static handoff record, not an everlasting lock; evaluate the linked PR and current HEAD; successors must avoid overlapping file edits without separately coordinating.
