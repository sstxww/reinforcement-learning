# R001 — independently attest exact-main postmerge CI

## Verified inherited work
- Read complete Gmail V7 TXT (32,014 bytes), GitHub repo permissions, V1 AGENTS/SESSION/CLOSED_LOOP protocols, main CI and train.yml, model registry, and current PR diff/evidence.
- Base main \`c1b828734527bae6141805581693d890cc3bff94\` had #165 least-privilege PPO/publisher separation already integrated by another session; do not duplicate its workflow change. Subsequent main commits may occur at any time.
- Prior verified main \`3a745c6f6a48c65528bcbeb81b8627b8db93f046\` has SUCCESS Action #41511419671; \`c1b828...\` has SUCCESS #41512315964. These correspond to exact SHAs, never generic "CI green".
- Reviewed #174 (read-only Release inventory), which has exact-head \`874bbba4377c229c2218b565779dd4dc7d3b0104\` SUCCESS Actions #41511087345, own genuine baseline receipt seed 99431, eight independent file paths not overlapped by main through #164. Posted actionable PR comment #6586704592. No actual merges by this session.
- Global coordination Issue #182 confirms an outside PR merge happened during a valid CAS lease. Existence of \`coord/autotavern-main-integrate\` ref does not prove all sessions obey it; no main merging allowed without truly enforced entry.

## Distinct falsifiable hypothesis and implementation
**Hypothesis:** A green CI can be misattributed to the current main when head SHA moved, CI is pending, a PR-only run is green, or a necessary native-engine/full-match step was skipped. A read-only fail-closed helper with two main-head reads can reject these cases for further independent integration review.

Own new files:
- \`scripts/v7_main_ci_attestation_fea0d63f.py\`: queries exact main ref, filters only current SHA/main push and canonical CI workflow, rejects non-success/pending, verifies actual job and mandatory step conclusions, reads main again to reject drift. Outputs a verifiable run+job URL and limitations; never claims merge mutex, signed result, artifact byte verification or PPO ability.
- \`tests/test_v7_main_ci_attestation_fea0d63f.py\`: synthetic API fixtures for stale SHA, wrong event, incomplete steps, newer failed run, mid-audit main drift, missing job and authorization boundary. These fixtures are NOT real game receipts.
- \`.github/workflows/v7-main-ci-probe-fea0d63f.yml\`: read-only own-branch path-scoped one-shot trigger, pinned TavernGym engine, own eight-seat baseline seed 99743, <=50 minute job cap, 30-day Artifact; no automatic commit loop, registry write, checkpoint promotion or Arena.

## Real execution and constraints
- Independent actual workflow https://github.com/sstxww/reinforcement-learning/actions/runs/41513152839 was queued at first observation; no pass/fail or game rank asserted until job output can be verified.
- If it completes: copy actual unmodified receipt from job/artifact into this session's \`experiments/\` path; assert complete eight-seat permutation, seed, engine, identity, zero truncation, no guard. This game is baseline infrastructure, NOT pure PPO skill.
- New MaskablePPO training steps **0**. Existing registered Latest unpromoted 1408-step Release SHA256 \`a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632\` remains owned by previous sessions. No new Release, no declared improvement, no Best/Champion, no formal Arena.
- Historical raw PPO eighth-place and incomplete-loop examples motivate stronger evidence gates, not a claim that this code fixes gaming skill.

## Integration gate and next action
Open an independent PR only after genuine own game evidence and tests; exact PR-head CI must run, then live-main compatibility and independent integrator review. Global exclusive merge right is **not** established (Issue #182); future integrator must revalidate merge-queue/exclusive lease enforcement before any merge and verify postmerge main SHA CI. If own Action cannot run, document blocked_with_evidence and preserve code + test regressions without misreporting a completed game.

## Verified real execution update (2026-11-02 19:51 UTC)

- Our exact source commit `b71bfc9594999b5e610dfbb51b16f7a9f097c515` triggered [Action #41513152839](https://github.com/sstxww/reinforcement-learning/actions/runs/41513152839) **COMPLETED SUCCESS**, job `125509849857`.
- Actual runner logs show `................. [100%]` = **17 synthetic negative/positive regression tests passed**. The live GitHub CI attestation succeeded and was preserved verbatim in `reports/s-20261103-fea0d63f/001-main-ci-snapshot.json` (original SHA256 `bd1e5c284fbcae793cf1f5fbfefffdb1b8cb2a3372ae9b50fdc849b7ccb68f20`). It verified `main@c1b828734527bae6141805581693d890cc3bff94` -> [CI #41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964) success, every required step, at 19:49:15 UTC. It does not verify the CI Artifact bytes.
- Pinned engine bootstrap/contract and this session's own complete **eight-seat baseline** TavernGym match completed: `seed=99743`, `seat=0`, `policy=baseline`, `placements=[8,5,1,7,3,4,6,2]`, 14 turns, 73 decisions, truncated combat 0, no forced turn limit. Original authentic receipt, extracted from runner [Artifact #13173762874](https://github.com/sstxww/reinforcement-learning/actions/runs/41513152839/artifacts/13173762874), committed **byte-for-byte** to `experiments/s-20261103-fea0d63f/001-99743.json`, SHA256 `077a9aecb4621c08589254e7e4bcff7a0b7cb4cfecc1353bf4eeb5071e08fbb2`; actual JSON byte length 516. This baseline rank8 is NOT PPO competitive evidence.
- Source artifact expires 2026-12-02; ZIP SHA256 `294212987c986f8825ec706738d948fd84b8df151fea1f2092c92efe376ce76b`. Permanent GitHub text records preserve actual receipt and audit result; no large model binaries committed.
- Authored consolidated report `reports/s-20261103-fea0d63f/002-action-evidence.json`. **New PPO training steps 0; model-only complete games 0; new Release none; Best/Champion unchanged.**
- During work, existing non-Draft [PR #207](https://github.com/sstxww/reinforcement-learning/pull/207) introduced a *separate static, Artifact-aware* postmerge CI snapshot checker; this branch adds *live API fetch + second main-ref verification* but does **not** check Artifact presence. Integrator should review compatibility, avoid redundant canonical scripts and combine essential strengths rather than blindly merging two tools.
- Global main exclusive merge mechanism remains unproven ([Issue #182](https://github.com/sstxww/reinforcement-learning/issues/182)); this session did **not** merge, create/publish a candidate model, use an Arena or overwrite any other session.

**Exact next action:** submit non-Draft PR to `main`, ensure latest-head full-match CI and own receipt identity gate pass, compare #207 and latest main before any integration; coordinate with an actually-exclusive integrator. If globally serialized merge authority never becomes provable, hand off the reviewed PR without a competing merge.
