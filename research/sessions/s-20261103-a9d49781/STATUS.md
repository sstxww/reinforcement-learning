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
