# s-20261102-3e715bca R001 — V5 P0/P1 integration-first checkpoint preflight

## Scope and current evidence (2026-11-02)

- Base main: `db5e23ae8c218808821327d806b05d2604cfadfb`; exact main CI [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040) **success**.
- This session read the complete 953-line V5 Gmail TXT, inventoried all **75** then-open PRs, latest main Actions and GitHub Releases. **74 Draft, one non-Draft #15**. No pending PR was safe to merge without resolving authored gates, dependency, current-main compatibility and/or duplicative code.
- Concrete P0 GitHub reviews: [#93](https://github.com/sstxww/reinforcement-learning/pull/93#issuecomment-6577726399) contains tests hardcoded for four registry candidates while main has five; [#15](https://github.com/sstxww/reinforcement-learning/pull/15#issuecomment-6577727170) is stacked on still-Draft PR #9, with no measured V1→V2 placement gain. No merge was attempted.
- Main registry: `models/registry.json`, `best=null`, `champion=null`, latest *unpromoted* 1,408-step candidate `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; reported paired model ranks [8,8,8] vs baseline [6,8,8]. GitHub Release assets exist; **this session did not independently download/model-load/retrain their bytes**, and must not claim it did.

## Focused engineering change

Existing main `tavern_ai.train.run` checked checkpoint engine JSON but loaded PPO without first verifying ZIP structure, optimizer entry, ZIP CRC or embedded/checkpoint expected digest. Added `inspect_resume` using **existing** `tavern_ai.checkpoint_preflight.audit_archive`, not a second registry. It checks engine metadata and validates before SB3 deserialization. CLI `--resume-sha256` accepts an independent trusted Release digest; when absent, an embedded digest is a consistency check only; when both are absent, legacy schema1 archives get only structural/CRC verification. After PPO loading, saved steps must agree with metadata. Newly saved schema1 checkpoint metadata now includes the SHA256 of the output ZIP.

Seven offline synthetic fixture regressions cover healthy/legacy, tampered bytes, external digest disagreement, missing optimizer, inconsistent engine/step counter and missing files; **fixture ZIPs are not real learned policies**. An isolated push-only workflow with a path filter runs these tests on the pinned real engine, plays a complete baseline eight-player TavernGym game with seed 91130 and commits a genuine receipt if successful. No automatic write to main, no weights in Git, no workflow push loop.

## Training, model and rank-eight status

- This session PPO steps: **0**. No new candidate checkpoint, no Champion promotion.
- This session independently completed eight-player games: **0 at documentation time**; the isolated workflow must be checked before updating this number.
- Current rank-eight evidence elsewhere: [#103](https://github.com/sstxww/reinforcement-learning/pull/103) reports 0 model BUY across **521** legal-BUY states over 3 genuine guarded PPO games; [#107](https://github.com/sstxww/reinforcement-learning/pull/107) reports 46 forced BUY actions over 3 further games but all model and overridden games still placed eighth. This suggests **buy omission is observed but forcing purchases alone does not fix the rank**. Play/Cancel nonprogression is an evidence-driven next hypothesis, not an established sole causal mechanism. Both source branches remain Draft; no claim of direct independent replay in this session.
- Main `.github/workflows/train.yml` still restores from a **90-day Action Artifact**, not reliably from a versioned Release. This PR improves checkpoint file validation but does **not** claim that unified durable mainline resume or paired eval is solved.

## Integration and acceptance

Keep Draft until independent exact-head PR CI plus own isolated workflow passes and authentic seed 91130 receipt is committed/validated. Do not merge without final-head diff, dependency/overlap review and current-main checks. Do not launch bulk PPO while persistent resume path and basic policy action failure remain unresolved. All official scored Arena matches remain prohibited.

Status: **engineering implementation submitted for CI; real-match gate pending verification**.
