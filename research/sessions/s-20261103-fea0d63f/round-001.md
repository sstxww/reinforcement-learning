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
