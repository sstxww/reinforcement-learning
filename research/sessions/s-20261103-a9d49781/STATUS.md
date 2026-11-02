# s-20261103-a9d49781 — V5 P0/P1/P2 integration status

- Session branch: `agent/s-20261103-a9d49781/optimization-001`; base main `c8b46a64628b2540c7b6d9f3fdc1458bfe9207c3`.
- Current status at initial commit: **running review / evidence gate pending**; no model improvement or checkpoint restoration claimed.
- P0: Reviewed live main, open PRs, exact-head CI, overlapping Release integrity/continuation PRs. #116 and #154 were already merged by OTHER sessions during this audit. No unsafe duplicate merge undertaken.
- P1: Main `train.yml` still has silent reset on missing/expired Artifact; central reliable Release-backed continuation and durable *output* publishing remain unresolved. Shared changes are contested by multiple Drafts; integration-owner selection needed.
- P2: Existing verified symptoms are raw PPO legal-BUY nonselection and action loops; #107 Buy override not a reliable rank repair. Own planned held-out seed 99361, baseline and unassisted V5 1408 model, no Arena.
- Model: `v5-s-20261102-68099929-1408-41428692617`, 1408 steps, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, **unpromoted**; Champion null.
- Own PPO steps: 0. New weights: 0. Own completed games at initial commit: 0. Subsequent workflow outcomes must be verified.
- Next gate: inspect own Actions status and receipts; update status only with genuine evidence; keep PR Draft while incomplete.

## Verified independent execution, 2026-11-03 / GitHub Actions
- Own actual workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41508290661 (result separately checked; never infer success from a queued job).
- Genuine same-seed TavernGym baseline: `experiments/s-20261103-a9d49781/001-baseline-99361.json`, seed 99361, **complete** eight seats, rank **8**, 13 turns, 52 decisions, no combat truncation/turn-limit end; 26 BUY-legal decisions, **14** actual BUY, no interventions.
- Genuine same-seed **raw unassisted V5**: `experiments/s-20261103-a9d49781/001-model-99361.json`, Release weights SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, complete eight seats, rank **8**, 14 turns, 121 decisions, no forced guard; 37 BUY-legal decisions, **0** actual BUY, 38 Refresh, 70 Freeze, 1 Play, 1 Sell.
- Paired mean rank delta candidate minus baseline = **0** (n=1); does not establish improvement. Correlated action-level BUY-exposure counts are not independent strategic opportunities.
- Release SHA256, archive/optimizer gate and CPU load step succeeded in the same workflow before games. This step is not a new optimizer continuation.
- Own PPO steps: 0; new model weights: 0; durable original Release reused, not rewritten; Champion and Best remain null.
- [Draft PR #162](https://github.com/sstxww/reinforcement-learning/pull/162). Keep Draft pending final-head PR CI and independent review.

## Main P1 integration advanced since initial snapshot
- OTHER sessions merged #125 (SHA-bound staged checkpoint writing) and #117 (manual-only main train.yml using canonical registered durable Release; explicit fail-closed restore; raw model canary, paired eval and unpromoted Release publication after gates). These supersede the original main silent Artifact reset risk documented above. Do not merge older conflicting shared-train variants over #117.
- Posted actionable blocking review on #149: https://github.com/sstxww/reinforcement-learning/pull/149#issuecomment-6586153916
- Independent model **optimizer continuation from newly restored published 1408-step Release** and subsequent save/re-download is not claimed in this session. Do not start unsupported bulk PPO.

## R002 — bounded canonical checkpoint continuation validation (P1)
- Started from **merged main #162**, SHA `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`; branch `agent/s-20261103-a9d49781/optimization-002`.
- Hypothesis: integrated #117 fail-closed registered Release restore plus #125 staged SHA-bound save really can recover the **same** 1408-step V5 optimizer, continue **exactly 128** steps, and retain a new immutable unpromoted candidate after independent real eight-seat model game and paired baseline evaluation.
- Distinct old Release `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; source weight not overwritten, no shared `train.yml` dispatch, no official Arena.
- Planned independent run seed 99367 for PPO learning, unassisted model full-game seed 99368, paired candidate/baseline evaluation seed 99369; aim 1408 → 1536 steps. The actual result must be read from own Actions and model hashes, not assumed.
- Separate publishing job owns short-lived write access and only uploads a unique **unpromoted** Release if training + model-only game + evaluation all complete; no Best/Champion promotion.
- At creation: **pending**, 0 new PPO steps and 0 new weights claimed for R002. Stop and record failure rather than silently reset or invent a match.

## R002 final audited outcome — **blocked_with_evidence**
- First canonical full run [41510156769](https://github.com/sstxww/reinforcement-learning/actions/runs/41510156769): true 1408 → 1536 PPO steps and persisted optimizer step counters 88 → 96 passed; new weight SHA256 `263eeeafb33eacc54d23d9154510843d28736887a46c7dba05217803d3b4d3eb` (not persisted as a Release). New raw model at seed 99368 raised `RuntimeError: Full-game safety limit exceeded`. Paired evaluation and publication were deliberately skipped.
- One meaningful failure-preservation workflow fix, not a blind PPO configuration retry: capture incomplete raw action metrics, upload failed-checkpoint recovery artifact, and store an explicitly **REJECTED** versioned Release after strict provenance checks.
- Reproduction run [41511033218](https://github.com/sstxww/reinforcement-learning/actions/runs/41511033218): training+optimizer advance passed; raw model game failed same safety limit. Diagnostic 6000-action probe **incomplete** at turn 8: Play 2782, Cancel 2775, Move 294, Freeze 80, Refresh 43, BUY 8; turn 8 alone has Play 2777/Cancel 2775. No complete candidate-controlled match receipt exists for R002.
- Rejected weight SHA256 `8ca9945226cf73f273f88a5301f522f5c388e6a53040707e267de35f38c9ea24`, parent `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, cumulative 1536, optimizer step counters 88 → 96. Source remains untouched.
- The **archive-rejected-diagnostic** job succeeded despite the overall workflow being correctly marked failed. Immutable prerelease with model.zip, metadata and checksums, downloaded and byte-compared: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-rejected-s-20261103-a9d49781-1536-41511033218
- Genuine persisted documents: `reports/s-20261103-a9d49781/002-resume-evidence.json`, `002-model-game-failure.json`, `002-incomplete-model-trace.json`. No fabricated `experiments/s-20261103-a9d49781/002-99368.json`, no strength estimate from incomplete game, no paired evaluation, no Best/Champion/Arena.
- **Do not merge R002 as a success or repeat larger PPO**; stop this failure signature after one genuine preservation fix. Next hypothesis: determine why raw Play/Cancel toggles yield a non-progressing policy loop and evaluate an isolated correction with verified game semantics, labeling any guard-assisted results separately.
