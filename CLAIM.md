# V7 atomic task claim — p0/v7-main-integration-entry

- Claim ref: `refs/heads/claims/p0-v7-main-integration-entry-001`; created successfully (exclusive creation of this ref, not exclusive main merge lease).
- Owner: `s-20261103-0a1a530f32`; Round: 001; Created on 2026-11-03 project local date; base main: `c1b828734527bae6141805581693d890cc3bff94`.
- State: `released_for_handoff` (owner has delivered PR #205 and original authentic game; latest-head CI and server-side enforcement remain integrator review tasks).
- TASK_KEY: `p0/v7-main-integration-entry`.
- Work branch: `agent/s-20261103-0a1a530f32/optimization-001`; proposed PR: https://github.com/sstxww/reinforcement-learning/pull/205.
- Owned files only: `scripts/v7_merge_safety_0a1a530f32.py`, `tests/test_v7_merge_safety_0a1a530f32.py`, `research/sessions/s-20261103-0a1a530f32/*`, `research/knowledge/proposals/s-20261103-0a1a530f32-001.md`, `experiments/s-20261103-0a1a530f32/*`.
- Evidence run: https://github.com/sstxww/reinforcement-learning/actions/runs/41513118163 (success; seven regression cases and complete baseline full game). Exact-head CI: https://github.com/sstxww/reinforcement-learning/actions/runs/41513964846 (queued at claim-note creation).
- Completion condition: own PR receives latest-head CI and review handoff, and task claim is explicitly marked released. **Never infer global integration exclusivity** from this claim.
- No lease over `coord/autotavern-main-integrate`; no other writer must wait for this claim to merge its independently reviewed work if a real server-enforced gate exists. However Issue #182 confirms such a gate was not proven as of inspection.
- Recovery: if the owner conversation stops, treat this claim as a static handoff record, not an everlasting lock; evaluate the linked PR and current HEAD; successors must avoid overlapping file edits without separately coordinating.

## Release and handoff
- Claim ownership voluntarily released by session `s-20261103-0a1a530f32` after pushing PR #205 and real receipt. This branch is an immutable task-claim history, not an active exclusion lock. A successor may explicitly take the outstanding integration-enforcement issue without treating this ref as a held global lease.
- The only outstanding automated gate is latest PR HEAD `f77321ca17a2ee21fe459e139516f144812f1a62` CI https://github.com/sstxww/reinforcement-learning/actions/runs/41513964846 (queued when released); inspect real result and reviewer state. Do not merge unless an enforced unique merge entrance has been proven.
