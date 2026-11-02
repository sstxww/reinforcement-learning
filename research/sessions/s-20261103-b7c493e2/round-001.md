# V7 round 001 — pre-learn resume metadata fail-closed gate

## Inherit and triage
Read latest Gmail V7 full TXT 32,014 bytes. Audited main `c1b828734527bae6141805581693d890cc3bff94`, `AGENTS.md`, existing release/registry, canonical `tavern_ai/train.py`, schema-2 tests, recent PRs #164 (merged), #167/#175/#181 (ongoing), and [issue #182](https://github.com/sstxww/reinforcement-learning/issues/182). A GitHub claim ref is owned by this session only, not a main mutex.

## Falsifiable hypothesis and code
Previously `build_checkpoint_metadata` tested schema-2 compatibility after `model.learn`. An invalid parent with a valid local SHA could be rejected *after* consuming PPO compute. Added `verify_parent_before_load` to reject malformed engine/schema/compatibility and integer fields **before** `MaskablePPO.load`. Independent `require_verified_resume` still checks checkpoint bytes SHA256. Existing post-learn metadata checks remain intact.

Synthetic tests build invalid parent metadata and replace model deserialization with a poison method, so success proves no PPO load was reached by that invalid input; synthetic fixtures are **not** trained weights, valid games, or evidence of competitive policy. Old schema-1 and valid schema-2 parents remain supported.

## Real execution
Source commits: [f5f982a](https://github.com/sstxww/reinforcement-learning/commit/f5f982a3a8338b8ddfb4d7f42cc0e757f82fb558) and [d56a7b6](https://github.com/sstxww/reinforcement-learning/commit/d56a7b68591643bfe35360d629fe8fb590831cdb). Independent bounded Actions [41513097226](https://github.com/sstxww/reinforcement-learning/actions/runs/41513097226), [41513121638](https://github.com/sstxww/reinforcement-learning/actions/runs/41513121638) queued at this snapshot; intended tests and real TavernGym baseline 99763, not a model game. Follow-up must append authoritative run/job evidence before claiming pass.

New PPO steps 0; new Release/model none; no new game receipt yet. Source durable unpromoted V5 1408-step Release remains registered as Latest, hash `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. No promotion, no Arena.

## Known limitation and next task
This guard validates metadata compatibility and hashes; it **does not** prove optimizer tensors can be restored or policy has learned to purchase. It does not create a global merge lock. Record genuine own game evidence, complete PR CI, then ask current exclusive integrator to review against the fresh main before merge.

## Completed original TavernGym proof and full-CI repair
- [Source workflow run 41513121638](https://github.com/sstxww/reinforcement-learning/actions/runs/41513121638) completed **SUCCESS** on fixed code HEAD `d56a7b68591643bfe35360d629fe8fb590831cdb`; pinned engine and complete own baseline battle validated. Downloaded original [artifact 13173782976](https://github.com/sstxww/reinforcement-learning/actions/runs/41513121638/artifacts/13173782976) and parsed exact JSON, not fabricated: seat 0, seed 99763, rank 3, full permutation [3,6,5,1,7,4,8,2], 66 decisions, turn 14, no truncation, 7 scripted opponents, TavernGym 1.1.0. Original JSON SHA256 `9585f7f6d3c7c3dcb60c09e0e4a645c182c6c0d862e548725a7119ced81f17f1`; committed to `experiments/s-20261103-b7c493e2/001-99763.json` after real source audit.
- First isolated [failure 41513097226](https://github.com/sstxww/reinforcement-learning/actions/runs/41513097226): bool schema treated as integer schema-1; corrected [d56a7b6](https://github.com/sstxww/reinforcement-learning/commit/d56a7b68591643bfe35360d629fe8fb590831cdb). Second source workflow passed.
- Initial full PR [CI 41513334215](https://github.com/sstxww/reinforcement-learning/actions/runs/41513334215) reported 391 passed, 1 skipped, 2 failed from old tests without schema; [5c38cab](https://github.com/sstxww/reinforcement-learning/commit/5c38cab0c093d904e2a698716f0a9330e285c4bb) adds schema-1 markers ONLY in synthetic fixtures. Existing tests still verify corrupt SHA and wrong loaded counter; production guard remains strict. See `failures/002-legacy-fixtures.md`.
- Training added **0** steps, no model run, no Release, paired n=0; baseline-only rank3 is never credited to PPO. Full PR current HEAD CI must finish before review-ready; main merge additionally needs enforced single entry. No private upstream or Arena write.
