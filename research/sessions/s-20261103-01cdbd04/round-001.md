# Round 001 — V7 serialized integration entrypoint

Hypothesis: 10-20 sessions sharing one GitHub account have no provable single-writer main merge authority. Green PR checks alone cannot safely authorize parallel merging.

Main base 990acd21d598a34a554a80c50089a8f1a9423ac4. Reused existing #117/#125 resume and persistence gates, #176 FREEZE evidence, #164 schema-2 optimizer lineage. PR #15 remains stacked on Draft #9, and recently green #179 cannot be blindly merged after main advances. Do not duplicate existing shared training/evaluation fixes.

Implement manual-only, branch-protected GitHub merge entrypoint with fixed concurrency group autotavern-main-integrate, exact head SHA, fresh main SHA, main ancestor requirement, no Draft, clean mergeability, complete successful latest-head checks, and exact-head review attestation. The endpoint never force pushes. A passing preflight never implies completed postmerge main CI. The new workflow is not dispatchable before it is integrated into the default branch.

New synthetic tests are *not* eight-seat games. Dedicated branch-only Actions canary requests TavernGym pinned baseline seed 99711, seat 0, 7 built-in opponents. Claim receipt only after original job and JSON complete. Our training=0 PPO steps, new model Release=none, model improvement=not assessed, Arena ranked=none.

Limitations: nonqueue direct merges remain possible for privileged clients; all agents must honor queue, or better enforce repository-level merge queue/branch rules. Repo-level constraints and real dispatcher permissions require integrator review. An attempted merge without valid CI and exclusive coordination remains forbidden.

Next step: verify run outcome, obtain genuine receipt if complete, review code, file non-Draft PR and run exact head PR CI, then route to exclusive integrator. No Champion promotion.
