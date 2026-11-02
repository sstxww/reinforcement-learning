# Round 001 — fail-closed V7 serialized merge entry

## Verified scope and hypothesis
Read full 32,014-byte V7 Gmail TXT, current main, AGENTS/session rules, CI/train workflows, registry and many competing PRs. Existing resume and provenance logic is already merged (#117, #161, #166, #169, #176); avoid duplicating these shared files. At the initial read, main was unprotected and Rulesets were empty. Other integrators moved main while prior-head PR CI completed. A passing old-base job is **not** validation of the current merge base.

Implement manual-only workflow with global `autotavern-main-integrate` concurrency, read-only preflight, explicit opt-in write job, exact current main/head SHA, fresh PR full-match CI **for the same base SHA**, observed unit/engine/real-game steps plus nonempty receipt Artifact, no Draft / unresolved blocking reviews, and conditional GitHub REST merge using head SHA. Inspect refs again immediately before merging. A successful merge still requires independent postmerge main CI before declaring integrated.

## Actual work and tests
Created atomic *task-only* claim `claims/p0-v7-serialized-pr-merge-entry`; dedicated branch. Implemented `scripts/v7_integrate.py` and eight synthetic regression cases. Isolated local pytest returned 7 pass / 1 fail: invalid repository path was accepted. Tightened `..` validation and re-ran **8 passed**, not a remote CI assertion. Implemented two GitHub workflows: manual serialized integration (inactive until merged into main) and own read-only, budgeted 45-minute baseline canary. Real cloud run https://github.com/sstxww/reinforcement-learning/actions/runs/41512746763 created, initially queued; do not infer game result.

## Training / game / model honesty
New PPO steps **0**, source model not loaded or resumed, no new checkpoint or Release, no Best/Champion change. Own planned eight-seat seed=982134 is **baseline infrastructure only**, not raw model comparison. Historic unpromoted V5 1408-step reference checksum `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, pin TavernGym 1.1.0 / source `6d8712c93022ba11`. No new controlled raw PPO rank, BUY rate, paired uncertainty or strength claims. If own run fails, save failure signature and no fake completed receipt.

## Security and next iteration
This manual workflow serializes only participants using it: a separate direct merge API, unprotected main or stale PR base remains an external risk. A reviewer must examine code and the new job's credentials; CI proof must cover latest PR HEAD and current main. Next: inspect original canary output, commit it if valid, obtain non-Draft PR and exact-head CI, compare current main, and hand off explicitly to an effective integrator. Do not self-merge on task-claim ownership.
