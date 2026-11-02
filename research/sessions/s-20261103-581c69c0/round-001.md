# Round 001 — precompute schema-2 failure gate

Base main `990acd21d598a34a554a80c50089a8f1a9423ac4`. V7 Gmail TXT (32,014 bytes) read completely. Another session merged #164 while this session reviewed it. Own task claim `claims/v7/train-schema2-prelearn-validation` successfully created atomically; no global merge lock acquired.

## Proven code risk
Current main #164 validates the parent's schema-2 compatibility inside `build_checkpoint_metadata` *after* `model.learn`; a SHA-bound but engine-contract-incompatible parent may still be deserialized and consume training before rejection. Call `preflight_resume_parent` after the existing archive digest check and before `MaskablePPO.load`. It reuses the same production metadata builder with a dummy +1 step counter only for structural validation; real steps and child metadata are still constructed after the actual learn call. A pure regression module covers matching/mismatching schema-2 and unsupported parents.

## Actual work and bounded evidence
Own code commit `ba4903a0f858e04a75d8f11de437a371542c7eaa`; synthetic tests commit `2717a700e72fbb59e4965b151d206b61e27cc23c`. Code not yet verified until Actions. No own new PPO steps/weight/game/release claimed at initial writing. Historical raw model rank-eight and buy-avoidance remain unresolved. This is not a policy-quality fix and cannot justify Champion promotion.

## Integration
#174 independent review posted (review ID 5742310376), #164 merged by someone else. No main push/merge by this session. Once own real baseline receipt is verified and PR-head CI passes, re-read main SHA and actual merge gate; only a valid exclusive integrator may merge. If training smoke or game fails, save true failure rather than fake placement.
