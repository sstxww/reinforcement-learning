# Round 001 — authenticated seat-3 receipt gate

- **SESSION_ID:** `s-20261103-f6994f077b`
- **TASK_KEY:** `v7/seat-attestation-integrity`
- **ROLE:** REPAIRER / EVALUATOR; no exclusive INTEGRATOR lease
- **ROUND:** 001; **state at initial write:** real-game CI running
- **BASE_MAIN_SHA:** `c1b828734527bae6141805581693d890cc3bff94`
- **Work branch:** `agent/s-20261103-f6994f077b/optimization-001`
- **Exclusive task claim:** `claims/v7/seat-attestation-integrity`, created successfully, claim record commit `b08d629f1f44ecf1de1a050927d8df2a827857ed`
- **Own code SHA:** `41d3417851293e429d7a726876266021ebaeb236`
- **Own synthetic test SHA:** `5cfda6dc50f0b892ec79eceb3f20a5371d207d4e`
- **Unique workflow SHA:** `e5ba83b7f60e3fe9d48252e557b6942a15f8dd6b`
- **Genuine run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41512909874
- **Main CI at initial synchronization:** https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964 — success for base main SHA
- **Recent merged PRs inherited:** #117 registered Release continuation, #125 staged checkpoint, #140/#152 canonical receipts, #154 model registry, #161 SHA digest guard, #162 rank-eight evidence, #164 schema2 resume, #165 train privilege separation. Never rewrite or count their results as ours.
- **Open PR audit:** #175 and #173 are still Draft and conflict/merge-gated. #175 is independently claimed by another active ref; do not override it. No main merge performed here.

## Hypothesis / intervention

Old canonical `validate_integrity()` permitted `seat=3, agent_placement=1` when `placements[3]!=1`, because it only checked the sorted eight-rank permutation. This is an attribution-integrity error at the receipt layer, not a demonstrated strategy-performance issue. Fix this by validating the real controlled seat and its placement, with backward compatibility for legacy seat zero.

The added test file provides negative mutation and positive backward-compatibility tests. GitHub run #41512909874 has a dedicated step for these tests and an independent real TavernGym 1.1.0 **baseline** game with seed 99841, controlled seat 3, seven scripted bots. Preserve the exact match only after `Game.is_over` and strict verification. No guard/fallback is permitted to masquerade as raw-model evidence.

## Model, budget and statistical claims

- Additional PPO training steps: **0**; no training workflow invoked.
- This session's model SHA, optimizer evolution, new checkpoint and Release: **none**. Registered historical V5 1408-step unpromoted Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617 ; historical SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Those weights are not involved in this isolated receipt-integrity fix.
- Authentic games by this session at time of writing: **0 completed verified**, game attempt currently executing, outcome unknown; synthetic tests cannot serve as game receipts.
- Independent baseline/model comparisons, top4, win rate, paired rank and statistical uncertainty: **not measured in this round**.
- Best/Champion promotion: **none**, no official Arena participation.
- Model-quality rank-eight root cause remains open (other sessions have already documented legal BUY non-use and HERO_POWER/PLAY/CANCEL loops). This change does not imply a cure.

## Failures and gates

- Could not read branch protection rules: GitHub connector returned `403 Resource not accessible by integration`. No proof of main merge lease/queue; **do not merge main**.
- Main `.github/workflows/train.yml` remains manual Release-restore; not touched.
- Actual full-match job outcome, generated artifact, latest PR CI, integrator review and postmerge main CI **not yet verified**. Do not claim any of them as success.
- No PR created at this timestamp. Open a non-Draft PR only when authentic receipt is committed and review-ready, then check latest-head PR CI.

## Exact next operation

Read GitHub Actions run 41512909874 jobs/logs. If it completes, extract the exact `AUTHENTIC_SEAT3_RECEIPT`, validate its SHA/seed/seat/model-policy/placements from original output, commit it under `experiments/s-20261103-f6994f077b/`, and update this status with immutable run URLs. If a genuine game fails, commit a failure note rather than a fabricated completed JSON. Create a reviewable PR and check all latest-head CI before any exclusive integrator merge. 

## Post-run verification — authoritative final round evidence

The preceding sections are a timestamped initial snapshot. The run subsequently **completed SUCCESS**; the original execution is [Actions #41512909874](https://github.com/sstxww/reinforcement-learning/actions/runs/41512909874), job `125509004790`. Synthetic integrity and seat-rotation regression steps passed; the pinned engine contract and genuine complete seat-3 baseline match passed independently.

- Real match: seed **99841**, controlled seat **3**, **original baseline** versus seven scripted TavernGym bots, **16 turns**, **40 seat-3 policy decisions**. Completed `Game.is_over()=true`, rank at seat 3 **8**; all placements `[5,7,6,8,1,2,4,3]`, `truncated_combats=0`, `turn_limit_end=false`. This is n=1 baseline CI evidence, *not* PPO strength.
- Original [Artifact #13174805676](https://github.com/sstxww/reinforcement-learning/actions/runs/41512909874/artifacts/13174805676) ZIP SHA256 `cf7371e06e90cce04d7f3d41107e18c804a54fab8195b1e71ceb2101440f35b0`, original 784-byte JSON entry SHA256 `bbde08a26895b54f4d6f7e396b29fd14ca7b4e04b67fe52690771af2f386aca1`.
- Authenticated source JSON was committed unmodified under [experiments/s-20261103-f6994f077b/001-99841-seat3-baseline.json](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261103-f6994f077b/optimization-001/experiments/s-20261103-f6994f077b/001-99841-seat3-baseline.json), commit [0a16860](https://github.com/sstxww/reinforcement-learning/commit/0a16860e9d5d1f88ffd638197abb31120e15a4c7). The original job log includes the exact receipt JSON after the new strict validator checked it. This is genuine fixed-engine match evidence; no regenerated/hypothetical data.
- PPO additional training steps **0**; new weight release/optimizer save **0**; raw model / assisted model games **0**. No independent candidate-vs-baseline comparison, hence no model promotion. Rank-eight model pathology remains open to separate P2 workers.

**Next required acceptance:** open non-Draft PR to main, check latest exact-head PR CI and conflicts, and hand over to an independently exclusive INTEGRATOR. GitHub read of branch-protection policy returned 403, so this Worker may not merge main on presumed privileges.
