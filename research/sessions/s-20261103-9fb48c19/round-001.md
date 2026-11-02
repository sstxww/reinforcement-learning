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

## Verified R001 outcome, negative experiment and causal distinction
- Scoped **8 pytest tests** passed in actual [first Actions #41513545167](https://github.com/sstxww/reinforcement-learning/actions/runs/41513545167); live GitHub audit concluded `merge_authorized=false`. Engine bootstrap / pinned contract / full eight-seat **baseline** seed 99731 passed. Original run overall failed only on push, **not on tests or game**.
- First original full-game Artifact #13174726922: SHA256 `e2e837724590e479e4d0291631554d9b13b744b6f79d17d3ad34a07bbe8104f8`, seed 99731 rank8 turns15 decisions42, actual completed. Failure signature from original run stdout: `! [rejected] HEAD -> agent/s-20261103-9fb48c19/optimization-001 (fetch first)`. Initial remote branch advanced while workflow was running. Root cause verified by job logs.
- Minimal fix commit [1842c2f](https://github.com/sstxww/reinforcement-learning/commit/1842c2f38dea8727c6ef7b732906a133d7f79fef): fetch/rebase own receipt commit onto current own branch HEAD and retry up to three times with **no force push**.
- Actual second [Actions #41514578194](https://github.com/sstxww/reinforcement-learning/actions/runs/41514578194) **completed SUCCESS**, all steps incl. own receipt commit. New original Artifact #13175232382 receipt SHA256 `1c07e2c72498e5c4247d8d45bf5ebee7988376d6305297077581b38b234a3b99`. Original genuine own receipt was committed at [63e66e7](https://github.com/sstxww/reinforcement-learning/commit/63e66e7b06b93926b2fc221a22af3dfb8490a4f4), under `experiments/s-20261103-9fb48c19/001-99731.json` and validated against complete eight-seat game contract. It is **baseline**, not model PPO.
- Actual new PPO steps=0, model checkpoint from this session=none, persistent Release=none, raw paired model games=0. No Best/Champion promotion.
- Current bottleneck is not syntax of the coordination ref: live audit records `main_not_protected`, `no_active_merge_queue_ruleset_observed`, `exclusive_merge_writer_authority_not_proven`. Issue #182 records a real direct-merge bypass during a valid CAS lease. A code-only gate that always denies cannot configure/enforce GitHub authorization.
- Compared existing rank-eight research: `reports/s-20261103-b642f1d8/001-raw-model-diagnostic-99384-verified-summary.json` reports no Buy and 70 Freeze on one unassisted rank8 game, while `reports/s-20261103-c1452513/002-1536-candidate-heldout-failure.json` records 128 additional PPO steps with raw candidate rank8 and incomplete heldout due safety limit. These are other sessions' evidence and don't prove Freeze is sole cause.
- Known PR guard-review gap: PR #172 `policy=model` + `policy_variant=baseline` is treated as raw without policy/variant consistency check; review submitted. #173/#177 duplicate same guarded-counter aliases. Need one consolidated vetted implementation after enforceable single writer.
