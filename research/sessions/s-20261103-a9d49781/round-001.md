# AutoTavern-AI V5 / s-20261103-a9d49781 / round 001

## Scope and ownership
- Authoring branch: `agent/s-20261103-a9d49781/optimization-001`; forked from main at `c8b46a64628b2540c7b6d9f3fdc1458bfe9207c3` on 2026-11-03.
- Read the Gmail V5 instruction TXT in full (27,248 bytes); writable repository **only** `sstxww/reinforcement-learning`.
- This session is **P0/P1 integration audit plus P2 genuine held-out behavioral replication**, not another PPO trainer and not an Arena session.
- No writes to the shared `train.yml`, model registry, other sessions, upstream simulator, or main. No Champion promotion.
- Planned independent game seed 99361, pinned TavernGym 1.1.0 source hash `6d8712c93022ba11`; feature/card/action dimensions 4017/447/245. Actual runs must be verified from GitHub Actions and own receipts, not assumed.

## Verified P0 inventory and concurrency notes
- At initial inventory, 115 open PRs (111 Draft). The non-Draft PR #15 targets `agent/learning/v1`, stacked on Draft #9, so not independently ready for main.
- While this session audited PRs, other integrators merged #116 (reuse strict checkpoint preflight inside canonical Release verification) and #154 (pool membership referential integrity) after #152 (receipt permutation safety). Never attribute those merges to this session.
- #130 is an overlapping Release verifier variant with different/lower ZIP/optimizer checks, and later reverted to Draft. Do **not** merge on top of #116 without isolating genuinely new tests.
- Draft #110/#117/#123/#127/#132/#134/#142/#147/#149/#151 all propose overlapping aspects of Release restore into the same main train pipeline. Require one integrator to select/extract a canonical implementation, validate existing schemas and immutable model provenance, and avoid combining competing shared-workflow edits.
- Draft #148/#137/#144 and others cover overlapping strict paired evidence. Main already has production evaluator receipt integrity from #153. Retain only nonduplicative uncertainty or seat-rotation changes after tests.
- Live main advanced continuously; use fresh head SHA, latest PR-head CI, genuine own receipt, and a single integration-owner transaction before any merge.

## Verified P1 gaps
- Main `.github/workflows/train.yml` restores a 90-day `v1-model` Actions artifact. If unavailable, it logs fresh initialization and clears checkpoint rather than failing closed. It does not select and validate an immutable Release as reliable restoration source.
- Main `tavern_ai/train.py` checks old sidecar engine equality before loading but does not enforce a trusted external SHA+archive optimizer preflight or cumulative-step/optimizer continuity by itself.
- `tavern_ai/checkpoint_preflight.py` already has strict SHA/schema/ZIP/optimizer checks, and #116 now composes this into `release_asset_verifier.py`; do not duplicate validators.
- `models/registry.json`: Best/Champion null, latest unpromoted 1408-step V5 Release `v5-s-20261102-68099929-1408-41428692617` weight SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Three held-out placements [8,8,8] vs baseline [6,8,8]. Other 1536-step unpromoted experiments are **not** promoted merely because Releases exist.
- Future canonical continuation must verify weight bytes, metadata, engine, model CPU load, actual optimizer continuation, saved new bytes/hash, full unassisted model match, independent comparison, and durable storage. A downloadable Release by itself proves none of those latter gates.

## P2 evidence already in main / draft research (NOT causal verdict)
- Existing V2 raw games: 74 decisions where BUY was mask-legal, zero actual BUY, ranks [8,8] vs baseline [6,7], with many Refresh/Freeze choices.
- Existing V5 1408-step raw game: 35 BUY-legal decisions, zero BUY, rank eighth. Evidence counts temporally correlated decisions, not independent optimal buy opportunities.
- An **incomplete** raw V2 trace had 2,978 hero-power and 2,977 cancel decisions; it is not a completed-game receipt.
- Draft #107 (stacked on #103) reports 46 forced purchases in nine real games, but three corresponding candidate arms still rank [8,8,8]; explicit intervention is **not** PPO improvement.
- Testable bottlenecks: action-family collapse, legal buy opportunity utilization, public observation progress, hero-power/cancel oscillation, and board development. Do not speculate that training length or reward alone caused the outcome.

## Independent workflow gate
The own isolated workflow `.github/workflows/v5-evidence-s-20261103-a9d49781.yml`, when created, attempts trusted 1408-step Release download, real CPU load and one same-seed baseline/model comparison using existing `tavern_ai.buy_opportunity_68099929`. It must preserve only authentic complete receipts, and report any model timeouts as failures rather than fabricated completed results.
**Execution state at initial authoring: pending; zero new PPO steps, zero new weights, zero new games claimed.** Actual status must be updated only after inspecting run and receipts.

## R001 verified result — full-game heldout pair, seed 99361
- GitHub Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41508290661; original workflow commit `70ed5b05cbd4333c99a3cba840046e09d7c7f09f`.
- Exact source Release: `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, cumulative original 1408 steps. GitHub workflow strict hashed ZIP/optimizer/CPU load gate passed.
- Baseline genuine game: `experiments/s-20261103-a9d49781/001-baseline-99361.json`; seed 99361, controlled seat zero rank 8, 13 turns, 52 decisions, final placements [8,2,1,6,7,3,5,4], 26 legal BUY decision exposures, 14 actual BUY, zero forced ends, no truncated combats.
- Unassisted model genuine game: `experiments/s-20261103-a9d49781/001-model-99361.json`; same seed and controlled seat zero rank 8, 14 turns, 121 decisions, final placements [8,5,2,3,1,4,6,7], 37 legal BUY decision exposures (7 distinct turns), **0 actual BUY**, 38 rerolls, 70 freezes (action ID 2 classified `other` by the reused diagnostic's coarse family helper), 1 Play, 1 Sell, zero guard/fallback, no truncated combats. Early public trace contains many empty-board states.
- Mean placement baseline=8, model=8, paired delta=0, n=1. This is descriptive confirmation of a policy action-economy failure, not significance or an established root cause. The baseline also ranked eighth this time; buying alone cannot be asserted to improve placement.
- Code/integration actions: created own isolated workflow and full research handoff, and submitted PR #149 review; [Draft PR #162](https://github.com/sstxww/reinforcement-learning/pull/162). Other integrators merged main #116, #154, #125 and #117 in parallel; not our merges.
- Own training steps 0; produced weights 0; source Release untouched; no model promotion, no Arena. Further PPO expansion withheld until persistent optimizer restoration and evidence-backed action-progress intervention. Do not infer reliable generalized strength improvement from one pair.
