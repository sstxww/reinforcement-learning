# V5 Session s-20261102-71136659 — Round 001 (P0–P3)

## Authenticated instruction and isolated ownership
- Gmail V5 message dated 2026-11-02, complete 27,248-byte TXT read. Only write target: `sstxww/reinforcement-learning`; no Arena ranked, no upstream writes, no local A11 or desktop control.
- Isolated branch: `agent/s-20261102-71136659/optimization-001`. Original main HEAD: `db5e23ae8c218808821327d806b05d2604cfadfb`.
- Concurrent main advanced during work to `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`; this is not a rebase or merge.
- Work never modified main, other sessions' refs, their artifacts, or the official shared `train.yml`.

## P0 — actual PR inventory and blockers
- First REST snapshot: 75 open PRs, 74 Draft. A later snapshot during concurrent integration contained **81 open, 80 Draft**; canonical audit JSON: `reports/s-20261102-71136659/001-open-pr-audit.json`. All five buckets are provisional queues, not reviewed green merge decisions.
- The sole non-Draft PR #15 targets `agent/learning/v1` rather than main; it depends on #9 (Draft). Its PR description still says to remain Draft until independent CI/review, notwithstanding current metadata. **Do not merge #15 ahead of #9 or bypass the author's stated gate.**
- Release/resume/registry drafts #82/#84/#86/#91/#93/#94/#95 partly overlap already integrated provenance modules. Review changes against current main, don't bulk-merge duplicates.
- Negative or inconclusive experiments do not justify policy replacement (e.g. #60, #65, #71). Full per-PR CI/latest SHA and conflict verification remains pending; nothing is asserted safe to merge.
- Previous successful main CI run was [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040) for original main SHA. It is not a passing CI receipt for this branch.

## P1 — training and archive reality
- Main `tavern_ai/train.py` saves `model.zip` plus engine metadata and does actual MaskablePPO continuation.
- Main `tavern_ai/evaluate.py` compares seeded full matches but lacks explicit paired per-receipt identity, weight lineage and fallback-disclosure gates.
- Main `.github/workflows/train.yml` resumes from a 90-day Actions Artifact or restarts fresh. It does **not** automatically resume from an immutable GitHub Release. Don't label that main workflow durably continuous.
- `models/registry.json` latest is unpromoted `v5-s-20261102-68099929-1408-41428692617`, 1,408 reported steps, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; no Champion. The published Release asset is listed in GitHub; our independent binary redownload/resume is delegated to isolated run [41449601213](https://github.com/sstxww/reinforcement-learning/actions/runs/41449601213).
- A public Release listing and earlier repository claim are not substituted for our own successful byte verification.

## P2 — eighth-place evidence is not just low train steps
- Real seed 99128 in `reports/s-20261102-68099929/003-buy-opportunity.json`: raw 1408-step model 0 BUY / 35 legal BUY decision states; baseline 14 BUY / 21 legal BUY decision states. One paired seed gave rank 8 for both. These decisions are correlated and legality does not establish optimality.
- Raw 1280-step probe `reports/s-20261102-ba09e2d4/002-action-opportunities.json` timed out with 2,978 HERO_POWER and 2,977 CANCEL actions, 0 BUY, 10 legal-buy decision opportunities, and no finished match. It is NOT a rank result.
- Separate guarded two-seed report `reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json`: candidate ranks [8,8] vs baseline [5,7], with 4/0 guarded interventions; fallback must never be mixed with raw-model evaluation.
- Root-cause hypotheses: action-oscillation collapse and failure to exploit *legal* purchase opportunities. Causal attribution and economy/value optimality remain unproven.

## P3 — actual isolated work
- Committed `tavern_ai/paired_evidence_s71136659.py`: strict existing-receipt paired check, policy/engine/seed/seat/model-hash validation, duplicate prevention, raw-vs-guarded failure, per-pair descriptive rates and exploratory bootstrap CI. No auto Champion promotion.
- Committed `tests/test_paired_evidence_s71136659.py` (synthetic tests, **not real game evidence**) and independent fixed-budget workflow `.github/workflows/experiment-s-20261102-71136659.yml`.
- Real GitHub Actions run: [41449601213](https://github.com/sstxww/reinforcement-learning/actions/runs/41449601213), launched by first branch push, executes tests, pinned engine setup, own baseline full game seed 99371, exact 1408-step Release checksum, 128 actual PPO steps if compatible, model-controlled game plus paired baseline seed 99373, and then unpromoted Release if all gates pass.
- Automatic repeated push trigger was removed after starting the initial run, preventing accidental duplicate training on documentation commits.

## Hard evidence gate and next moves
- No new steps, games or Release will be claimed until the run finishes and artifacts/logs have been inspected. If any step fails, capture precise failure and mark its status.
- Do not promote candidate based on n=1 paired sample; no Champion.
- Validate and commit the genuinely generated own receipt, status and outcomes; create integration PR with exact latest-head CI after that. If the engine/Release or model game fails, preserve failure evidence instead of fabricating a receipt.
- Prioritize a verified durable canonical Release fallback for main `train.yml` as a separate reviewed integration, not a blind overwrite of others' concurrent experiments.
