# Round 001 — precompute schema-2 failure gate

Base main `990acd21d598a34a554a80c50089a8f1a9423ac4`. V7 Gmail TXT (32,014 bytes) read completely. Another session merged #164 while this session reviewed it. Own task claim `claims/v7/train-schema2-prelearn-validation` successfully created atomically; no global merge lock acquired.

## Proven code risk
Current main #164 validates the parent's schema-2 compatibility inside `build_checkpoint_metadata` *after* `model.learn`; a SHA-bound but engine-contract-incompatible parent may still be deserialized and consume training before rejection. Call `preflight_resume_parent` after the existing archive digest check and before `MaskablePPO.load`. It reuses the same production metadata builder with a dummy +1 step counter only for structural validation; real steps and child metadata are still constructed after the actual learn call. A pure regression module covers matching/mismatching schema-2 and unsupported parents.

## Actual work and bounded evidence
Own code commit `ba4903a0f858e04a75d8f11de437a371542c7eaa`; synthetic tests commit `2717a700e72fbb59e4965b151d206b61e27cc23c`. Code not yet verified until Actions. No own new PPO steps/weight/game/release claimed at initial writing. Historical raw model rank-eight and buy-avoidance remain unresolved. This is not a policy-quality fix and cannot justify Champion promotion.

## Integration
#174 independent review posted (review ID 5742310376), #164 merged by someone else. No main push/merge by this session. Once own real baseline receipt is verified and PR-head CI passes, re-read main SHA and actual merge gate; only a valid exclusive integrator may merge. If training smoke or game fails, save true failure rather than fake placement.

## Final real results / negative finding

- Own real full eight-seat baseline seed 97831 rank8, true raw model seed 97832 rank8; both complete, original receipts from [run 41512678144](https://github.com/sstxww/reinforcement-learning/actions/runs/41512678144).
- Verified +128 actual PPO optimizer continuation from 1408 to 1536; model SHA256 `d6771d4439d1deb64231edd4caaf9ebbc8cd2f8db667c94b19a8c144b968b096`; source SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. ZIP CRC, real `policy.optimizer.pth`, CPU inference and own real model full game verified. Not a trained-policy improvement.
- Independent same-seed paired run [41513659254](https://github.com/sstxww/reinforcement-learning/actions/runs/41513659254): model `[8,8]`, baseline `[2,6]`, pairs n=2, rank delta +4.0 (worse). No model promotion; raw-only model, no fallback or guard. Original receipts and report under session-specific paths.
- Durable [REJECTED Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v7-rejected-s-20261103-581c69c0-r001-d6771d4439d1): model ZIP+metadata, three extra real game receipts, two-pair summary and checksum assets, re-downloaded and binary-compared to prepublish ZIP. Remote asset API SHA matches. Canonical registry, Best, Champion unchanged. Model research outcome is negative; revisit policy action economy, END progression and legal BUY selection instead of adding blind steps.
- Failure correction: earliest [CI 41512804901](https://github.com/sstxww/reinforcement-learning/actions/runs/41512804901) showed one invalid synthetic parent fixture, 393 pass/1 fail/1 skip; changed fixture only, no production safety bypass; subsequent [CI 41513155849](https://github.com/sstxww/reinforcement-learning/actions/runs/41513155849) had 394 pass/1 skip but predated genuine receipt commit. A later [CI 41513262104](https://github.com/sstxww/reinforcement-learning/actions/runs/41513262104) succeeded with its exact then-current commit; NEW final-head CI remains mandatory before integration.
- The two own test workflows are removed from final PR diff after authentic runs; no persistent workflow triggers left to generate repeating jobs. Next round should measure action-state stagnation and masked BUY opportunities on independent seeds, not claim new strength from n=2.
