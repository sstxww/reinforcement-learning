# Round 001: integrate historical two-asset Release verifier, without stale fixed-size registry

## Source, scope, and authorization
Session `s-20261102-d5349678` · branch `agent/s-20261102-d5349678/optimization-001` · PR [#136](https://github.com/sstxww/reinforcement-learning/pull/136).
The user's Gmail V5 TXT was completely read. Only `sstxww/reinforcement-learning` has been written; no upstream AutoTavern, ranked Arena, local A11 or other session branch modifications.
Started with main `db5e23ae8c218808821327d806b05d2604cfadfb`, CI [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040) success; concurrent main advanced through `ef77ae6bc5d9bef09e903fac7705917ec3b7366d` to `e1ef0f37497505f0f2902843af1bfdc15ebd198a`. A fresh exact-main check is required at merge time.

## P0 integration work actually completed
- Audited 75 open PRs at start (74 Draft); only non-Draft #15 depends on still-Draft #9 and targets its branch, so was not safe to merge into main.
- Inspected exact #93 head and its passing older-context PR CI [41429285964](https://github.com/sstxww/reinforcement-learning/actions/runs/41429285964), source verifier, test and valid original baseline game seed 91031. #93 had four pinned metadata hashes, and a test that erroneously required precisely four candidates, while current canonical registry has five.
- Created isolated branch **from** #93 head instead of modifying author's branch. Fixed the brittle test to compare record count to `len(data["candidates"])`, require `set(METADATA_SHA256).issubset(records)` and latest ID membership. No duplicate registry or Champion role.
- Opened own Draft integration [PR #136](https://github.com/sstxww/reinforcement-learning/pull/136) and submitted [a source-backed technical handoff](https://github.com/sstxww/reinforcement-learning/pull/136#issuecomment-6577990159).
- Created finite own workflow `.github/workflows/integration-s-20261102-d5349678.yml` to run Python tests, pinned TavernGym install, a complete eight-seat baseline canary seed **94673** and strict receipt validation. It never runs official Arena.
- Initial own [Actions run 41450357747](https://github.com/sstxww/reinforcement-learning/actions/runs/41450357747) **failed** at test-file discovery: `ERROR: file or directory not found: tests/test_release_asset_verifier.py`. Its source branch was older than latest main; no engine/game/test success may be claimed. This is a branch/CI integration error, not the PPO model failure; it requires latest-main rebase/merge, **not training hyperparameter changes**.
- Reconciled latest main by creating fast-forwardable two-parent merge commit `638c0d4a1f3d20e95710bb504d8befd7346a6700`: all latest main contents plus the eight distinct inherited #93 and own integration files; thus latest test path exists. No main push, no other branch mutation.

## P1 / durable model audit
- Main `models/registry.json` is canonical; published latest experimental checkpoint `v5-s-20261102-68099929-1408-41428692617`, 1,408 actual cumulative PPO steps via V2 parent, weight SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Release metadata/hash data is source-backed; this session did **not** redownload or load model bytes, do independent optimizer resume, or produce new weights.
- Latest registered candidate three held-out results are rank [8,8,8] versus baseline [6,8,8]; no Champion or Best is justified.
- Audited original main `.github/workflows/train.yml` only restores expiring 90-day Actions Artifact `v1-model` and may silently initialize a new PPO if unavailable. Other active PR #110/#109/#111 work on this issue, so do not independently launch duplicative training or rewrite shared work.

## P2 real rank-eight evidence and limits
- [Main raw V2 PPO telemetry](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-ba09e2d4/002-action-opportunities.json): seed 87102, 6,000 genuine model steps, not a completed game, turn 3 stall; HeroPower 2,978, Cancel 2,977, Buy 0, BUY legal on 10 decisions.
- [Guarded paired complete games](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json): seeds 87102/87103, guarded PPO ranks [8,8] vs baseline [5,7], actual Buy [0,0], legal-BUY turns [7,6], fallback interventions [4,0]. Guarded ≠ raw-model performance; sample n=2 is descriptive only.
- [Draft PR #103](https://github.com/sstxww/reinforcement-learning/pull/103) independently reported 521 legal Buy decision states and 0 Buys across 3 guarded model games, ranks [8,8,8]; overlaps already integrated diagnostics. [Draft PR #107](https://github.com/sstxww/reinforcement-learning/pull/107) found 46 forced Buys still rank eighth; naïve purchase override alone is not established as a fix.
- Confirmed **behavioral failures**: model acts repeatedly without progression and ignores some legal Buy opportunities. Causality in reward/loss, card embedding, rollout or profitable choice remains unproven. Focus on opportunity-adjusted action telemetry and action-mask semantics; do not blindly scale PPO.

## Honest end-of-round accounting and handoff
Model training: **0 steps** by this session. Own completed model-controlled games: **0**. Own complete baseline canary: **not yet established** after first workflow failure. Own persistent new model: **none**. Our integration PR remains **Draft**, **not merged**. Main CI after merge cannot yet be claimed from this branch.
Next: repair/run original full game on latest main, save strict receipt, verify final HEAD and PR CI; compare with competing Release-verifier PR #116 and integrate only distinctly useful code; advance to P1 durable resume only after checks, then P2 targeted experiment before scaling.
