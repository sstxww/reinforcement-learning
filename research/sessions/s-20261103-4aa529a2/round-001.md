# R001 — early schema-2 training gate (real executed work)

Session `s-20261103-4aa529a2`, role REPAIRER, task `p1/schema2-prelearn-parent-validation`; base main `990acd21d598a34a554a80c50089a8f1a9423ac4`.

**Problem:** merged #164 produced schema-2 child metadata after `learn`; an invalid parent compatibility contract would reject only at save-time. The preflight check now precedes the PPO ZIP deserialization and training, preserving the independent SHA-bound verification and save-time constraints.

**Executed:** GitHub branch commit `8e5267ee142684f94197c485864d456f547c27b9` introduced minimal code, synthetic invalid-parent regressions and bounded, read-only session-specific Actions. [Run 41512413873](https://github.com/sstxww/reinforcement-learning/actions/runs/41512413873) **SUCCESS**, test-install step and real engine install passed, real TavernGym full eight-seat baseline passed. Downloaded original [artifact 13173194839](https://github.com/sstxww/reinforcement-learning/actions/runs/41512413873/artifacts/13173194839), inspected game output and committed receipt at `experiments/s-20261103-4aa529a2/001-94837.json`. Policy baseline, seed=94837, controlled seat=0, rank=7, 57 decisions, 15 turns, eight-rank permutation [7,8,2,3,4,5,6,1], no truncation.

**Evidence type:** engineering baseline only; not candidate PPO strength. New training steps 0, no new optimizer/checkpoint/Release, no statistical comparison; `best` and `champion` remain unchanged. Existing registered 1408-step V5 SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.

**Improvement gate:** latest-head PR CI and explicit integrator serialization are not proven at this stage; no merge claim. Since branch protection API returned 403, cannot infer permissions or bypass review.

**Next:** PR ready only after latest-head CI and reviewer approval; serialized integrator verifies current main and merged code then postmerge main CI. If any regression fails, fix within 2 meaningful attempts or record it as blocked.

## Actual first PR CI failure and fix

[CI #41513176363](https://github.com/sstxww/reinforcement-learning/actions/runs/41513176363) failed with 396 passed/1 skipped/1 failed before engine setup. The legacy `test_refuse_wrong_step_count_after_load` fixture omitted `schema`, now strictly rejected before deserialization. Retained strict fail-closed production behavior; added schema-1 declaration to that synthetic fixture so the later saved-step mismatch remains tested. One meaningful fix attempt; next observe the new exact-head CI and full-match gate. No fake game receipt from the failed PR run.
