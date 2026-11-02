# V5 Round 001 — independent Release-to-registry drift inventory

## Scope and provenance
- Session: `s-20261103-ad1c30ff`.
- Repository: https://github.com/sstxww/reinforcement-learning
- Base main at branch creation: `df07dd23c99079449417fa8e645cf2b6c76b9704`.
- No direct main push; no changes to shared trainer, evaluator, registry, checkpoint, or other session branch.
- Pinned TavernGym expected by existing project: 1.1.0, observe2 (4017 floating features / 447 cards / 245 actions), engine hash `6d8712c93022ba11`.
- Training steps in this session: **0**; PPO checkpoint generated here: **none**; best/champion change: **none**.

## P0 integration work
- At start of review, main `e837e7b445cfb74a84fdb871a4bae4ec9e0ce034` advanced during audit to `df07dd23c99079449417fa8e645cf2b6c76b9704`. PR #157 fixed default 100-PR audit cap, had a successful latest-head full-match CI and an authentic eight-seat baseline receipt. Another integrator merged #157 while we rechecked main, so we did NOT race or merge it twice.
- PR #15 targets the not-yet-integrated branch of draft #9; therefore it is NOT an independent main merge candidate.
- Trainer and Release continuation drafts overlap current main and each other; no blind aggregation.

## P1 specific resolved gap in this branch
- Current `models/registry.json` contains five candidate records, designated Latest an **unpromoted** 1408-step model. Public GitHub Releases already contain additional later experimental model ZIP/metadata pairs. Merely discovering a Release must not update Latest or produce an unearned Champion.
- Added standalone read-only discovery CLI `scripts/v5_release_discovery_ad1c30ff.py`: GitHub Releases REST pagination (bounded 10 pages, no partial-success claims), registration cross-reference, missing registered releases, unregistered ZIP + metadata names, explicit no-verified-by-audit fields.
- New synthetic tests cover 101-record pagination, fail-closed cap/duplicate/malformed responses, missing registered Releases, unregistered newer candidates, and forbidden automatic promotion.
- Does not download weights, claim SHA verification, use training secrets, run PPO, change registry, or assert latest candidate is stronger.
- CLI: `python scripts/v5_release_discovery_ad1c30ff.py --out reports/s-20261103-ad1c30ff/remote-release-audit.json`. Output is evidence-only, not a training input.

## Engine/CI verification
- Dedicated push-only source validation: https://github.com/sstxww/reinforcement-learning/actions/runs/41509414911, triggered from `95ca68f57f330c5f1c08550ba798e2cc0ff742fb`. It runs standalone tests, discovers Releases, bootstraps the exact engine, and attempts its OWN complete eight-seat baseline game seed 99431.
- At documentation creation, success / placement / completed status **not yet observed**, so no receipt is claimed in this report. A future update must give exact original Action URL and validated JSON if run succeeds.
- Generic branch CI and any model-only match must be separately validated; an infrastructure baseline is not PPO-strength evidence.

## P2 rank-eight evidence and unresolved causality
- Canonical registry reports historical heldout raw latest 1408-step candidate ranks **[8,8,8]** versus same-seed baseline **[6,8,8]**. Best/Champion absent. It is a verified *registry record*, not newly run here.
- Prior model behavior investigations report a high proportion of legal BUY opportunities ignored, repeated REFRESH/FREEZE and unproductive actions. Yet separately reported forced-BUY ablations did not fix rank eighth. Thus BUY avoidance is a reproducible symptom but not yet proven to be the only cause.
- A decisive next comparison needs raw policy complete games with per-turn money, legal-buy exposure, BUY/PLAY/CANCEL sequence, effective board growth and turn-level state deltas, alongside unchanged baseline seeds. No increase in PPO budget before raw evidence and durable recovery.

## Model custody
- The registered historical 1408-step Release tag is `v5-s-20261102-68099929-1408-41428692617` with declared SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- This session has NOT performed its own Release asset redownload, independent hash/CPU/optimizer-state checks, or subsequent PPO training; report that gap explicitly.
- GitHub Actions temporary Artifacts are not equivalent to permanent Release custody.

## Handoff and gates
Only after own workflow success and committed genuine game receipt plus exact-final-head PR CI may integrators consider this discovery tool for main. The script is deliberately read-only and has no automatic merge or model promotion. Do not start large-scale training or formal Arena ranked games from this audit.

## Verified execution update (2026-11-02T19:26 UTC)
- **Successful own independent GitHub Actions #41509414911**: package/test dependencies installed, Release discovery test suite green, public Release API audited, pinned native TavernGym installed, own real eight-seat baseline game completed. Original source job `125497063105`; original receipt from uploaded Artifact `13171299050` was read from its ZIP and committed without altering JSON content at `experiments/s-20261103-ad1c30ff/001-99431.json`.
- Seed **99431**, controlled seat 0 place **8**, 17 turns, 51 actions, placements **[8,4,5,2,3,6,7,1]**, `completed=true`, no combat truncation or turn-limit ending. Baseline smoke, **not** model evaluation.
- Release scan actually returned **25** published tags: canonical registry lists **5** candidates; **20** other published tags have ZIP and metadata filenames; 0 canonical candidate tags missing. This is discovery, not independent byte, ZIP/optimizer, inference or training validation. Compact actual snapshot `reports/s-20261103-ad1c30ff/release-drift-summary.json`; full raw JSON from temporary workflow Artifact.
- Further historical **rank-8 evidence report** committed `reports/s-20261103-ad1c30ff/rank8-evidence.md` with checkpoint separation, no-buy-when-legal, raw loop noncompletion and forced-BUY negative ablation.
- This round added **0 PPO training steps, 0 model-only matches, 0 new model Releases, and 0 Champion promotions**. Do not confuse genuine baseline rank8 with model result. Next gate is final-head PR CI on a clean, non-overlapping integration branch and independent review.

## Final-head PR gate and live merge safety (latest observed)
- Our actual PR [#174](https://github.com/sstxww/reinforcement-learning/pull/174) latest head `91bda1f415643723ee638b82475c312a130421fa` passed **complete PR CI** [run 41510487353](https://github.com/sstxww/reinforcement-learning/actions/runs/41510487353): unit+PR evidence, exact pinned TavernGym, genuine eight-player independent CI match and successful evidence preservation.
- While checking this success, other sessions advanced main to `c5edec2e3261dacdf3908796ebfe0457fb76c02e`; latest main CI [41510861696](https://github.com/sstxww/reinforcement-learning/actions/runs/41510861696) was still in progress. That commit modifies main train.yml and other session paths, not our new module/tests/report/receipt, but any merge needs current-main compatibility verification and reliable integration ownership. **No PR #174 merge is claimed** at this checkpoint.
