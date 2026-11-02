# Round 001 — V7 merge-authority audit and existing restore PR review

Session `s-20261103-9fb48c19`, TASK_KEY `p0/v7-merge-authority-audit`, own branch `agent/s-20261103-9fb48c19/optimization-001`, base main `c1b828734527bae6141805581693d890cc3bff94`.

## Inherited validated evidence

- Current main [CI #41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964) SUCCESS at exact main SHA. Main `protected=false`, so cannot infer enforced global merge serialization.
- [Issue #182](https://github.com/sstxww/reinforcement-learning/issues/182) recorded a CAS coordination ref held while another session merged PR #164. A branch lease only excludes other clients that obey it.
- PR #161 and #164 were integrated by *other sessions*; latest production trainer has schema-2 provenance and SHA-bound resume guard. Production `train.yml` is manual-only; repeated unchanged bulk PPO is not justified.
- Canonical registered unpromoted V5: 1408 PPO steps, source digest `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; existing rank-8/nonprogress studies are historical, not this session's newly trained model. No Champion or Best.

## Actual actions (no fabricated future results)

1. Fully read Gmail V7 text (32,014 bytes); audited main, PR backlog, CI, Release registry and known CAS bypass.
2. Created atomic task claim `claims/p0-v7-merge-authority-audit` and isolated branch from exact main.
3. Wrote source-scoped `scripts/v7_merge_authority_audit_s_20261103_9fb48c19.py`, which uses only GitHub GET reads and **always denies issuing merge authority**. It checks fresh branch protection, PR base/draft/state/head/CI and queue-like ruleset hints. An apparent queue cannot prove non-bypassable direct merges.
4. Added eight synthetic test scenarios at `tests/test_v7_merge_authority_audit_s_20261103_9fb48c19.py`, including exact PR-head CI mismatch, incomplete runs, ruleset bypass actors, draft/wrong base, live 403 and held CAS lease insufficiency.
5. Submitted an actual review on [PR #175](https://github.com/sstxww/reinforcement-learning/pull/175) (review ID 5742369063) identifying the untested `samefile`→`unlink` race in its no-clobber restore rollback. This is a credible potential race, not an observed production exploit.
6. Triggered unique [Actions #41513545167](https://github.com/sstxww/reinforcement-learning/actions/runs/41513545167) to execute tests, read-only PR authority probe and pinned-engine complete eight-seat **baseline** seed 99731. At time of writing it was queued, no pass/game receipt assumed.

## Controlled test / train / promotion

- Own trained PPO additional steps: **0** (focused on highest-priority merger safety and a live Release restore PR review).
- Own verified full-game samples: **0 pending actual Actions result**. Planned canary is baseline-only, not model or competitive evidence.
- No candidate weights, optimizer changes, new persistent Release, Arena result, Best/Champion promotion, or own merge.
- Issue to resolve for global integration: protect main and enforce one actual non-bypassable merge entry; no script or CAS alone repairs repo-wide write governance. See Issue #182.

## Handoff

Read actual #41513545167 job steps and Artifacts. On success check JSON validation and immutable source receipt, then open a scoped ready-for-review PR and verify latest exact-head CI. On failure capture precise first error in `research/sessions/s-20261103-9fb48c19/failures/`. Another session must not represent this read-only audit as a working global merge mutex. After review/PR handoff mark claim released or handed off explicitly.
