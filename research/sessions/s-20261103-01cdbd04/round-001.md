# Round 001 — V7 serialized integration entrypoint

Hypothesis: 10-20 sessions sharing one GitHub account have no provable single-writer main merge authority. Green PR checks alone cannot safely authorize parallel merging.

Main base 990acd21d598a34a554a80c50089a8f1a9423ac4. Reused existing #117/#125 resume and persistence gates, #176 FREEZE evidence, #164 schema-2 optimizer lineage. PR #15 remains stacked on Draft #9, and recently green #179 cannot be blindly merged after main advances. Do not duplicate existing shared training/evaluation fixes.

Implement manual-only, branch-protected GitHub merge entrypoint with fixed concurrency group autotavern-main-integrate, exact head SHA, fresh main SHA, main ancestor requirement, no Draft, clean mergeability, complete successful latest-head checks, and exact-head review attestation. The endpoint never force pushes. A passing preflight never implies completed postmerge main CI. The new workflow is not dispatchable before it is integrated into the default branch.

New synthetic tests are *not* eight-seat games. Dedicated branch-only Actions canary requests TavernGym pinned baseline seed 99711, seat 0, 7 built-in opponents. Claim receipt only after original job and JSON complete. Our training=0 PPO steps, new model Release=none, model improvement=not assessed, Arena ranked=none.

Limitations: nonqueue direct merges remain possible for privileged clients; all agents must honor queue, or better enforce repository-level merge queue/branch rules. Repo-level constraints and real dispatcher permissions require integrator review. An attempted merge without valid CI and exclusive coordination remains forbidden.

Next step: verify run outcome, obtain genuine receipt if complete, review code, file non-Draft PR and run exact head PR CI, then route to exclusive integrator. No Champion promotion.

## Verified execution addendum — 2026-11-03 UTC+8

- Real code commits: 722fdd0f33fec8434a68297639e20afb56588100 (initial gate), 33596f6619ab03a469d72370722a342efedae75f (remove ambiguous gh check-run JSONL parsing), adba48119c53f4df25c18c841c8da0f8e6ae8f93 (original full-game receipt).
- Original own GitHub Actions: https://github.com/sstxww/reinforcement-learning/actions/runs/41512640097, job 125508130301, COMPLETED SUCCESS. All synthetic gate regressions, pinned TavernGym bootstrap, true eight-seat baseline match and receipt validation SUCCESS. This is not candidate PPO.
- Original ZIP artifact 13174505897 was downloaded and inspected; original JSON byte SHA256 5bd0c0da8a350b3d4268483bd15449e9a0be8da97339490894113e03dc7fc05d, committed unchanged as experiments/s-20261103-01cdbd04/001-99711.json. Seed 99711, controlled seat 0, completed true, 20 turns, 38 decisions, placements [7,8,2,4,1,5,3,6], rank7, zero truncated combats, no turn-limit end, engine source hash 6d8712c93022ba11.
- Non-Draft integration proposal: https://github.com/sstxww/reinforcement-learning/pull/197. No integration/merge of own PR and no main CI claim.
- Separate real review: PR #179 review id 5742384153 highlights moving-main CI coverage deficiency; no merge performed.
- By this session: 0 PPO steps; 0 raw-model games, 0 paired-model games, no candidate weight, no training Release, no model promotion. Existing registered Best/Champion remain not promoted by this branch.
- Main has advanced to c1b828734527bae6141805581693d890cc3bff94 (#165 Release privilege isolation) at this audit. Merge main into own branch without force before declaring PR current; exact live main must be checked again before any future integration.
- Critical blocker: no valid global exclusive integration authority; the proposed workflow is not yet on main, and its workflow concurrency does not fence all privileged external merges. Require latest-head PR CI plus review and genuinely serial integration prior to merge. Postmerge main CI is separately mandatory.
