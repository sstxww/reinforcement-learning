# Session status — s-20261102-9450775f

- Branch: `agent/s-20261102-9450775f/optimization-001`
- Base main: `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`
- State: **model archive + full real model-game audit verified**; PR integration and latest-head CI still require separate verification.
- V2 model Release `v2-learning-41413557445`: SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`; ZIP CRC and optimizer archive member passed, metadata cumulative timesteps 1280, pinned engine TavernGym 1.1.0 source `6d8712c93022ba11`, observe2 4017/447/245; Torch MaskablePPO load/predict succeeded. Actual incremental training in this session **0 steps**; optimizer restoration into `model.learn` not yet established.
- Model-only true full eight-seat game: workflow https://github.com/sstxww/reinforcement-learning/actions/runs/41427478915, seed 945077, **completed** with placement 8; 122 decisions, 16 final turns, buy 0, legal buy opportunities 37, refresh 41, other 71, end 7, upgrade 1, choose 2, zero forced end or baseline fallback, no truncation/turn-limit end.
- Independent baseline authentic game: seed 945078, **completed**, placement 8, 39 decisions, 15 turns, positions [8,5,7,1,3,2,6,4], zero guards.
- Canonical candidate model behavior report committed at `reports/s-20261102-9450775f/model-gate.json`. Genuine baseline evidence committed at `experiments/s-20261102-9450775f/001-945078.json`.
- Workflow **overall conclusion: failure** in **only the final evidence Git push** (non-fast-forward caused by own concurrently updated branch). All computation, tests and authentic games passed; see `failures/001-evidence-push-race.md`. Artifact #13132303660 is temporary, exact JSON restored to the branch via GitHub Contents API.
- The model rank-8 and buy=0 evidence alone cannot establish causality. 37 buy-legal opportunities do not necessarily mean 37 good purchases. Action IDs classified `other` still need their exact semantics decoded.
- Champion promotion: **false**. Best/Latest unchanged. No registered official checkpoint or new persistent training weights. No official Arena matches.
- P0 concurrency: during scan PR #43 and #25 merged independently; did not conflict or push to main. Audit is at `PR_AUDIT.md`.
- Next: fix end-step push race; require new actual latest-head CI; further no-fallback model-action/valid-gold semantic tests; only then consider incremental training.

## Verified final exact-action run (replaces preliminary other=71 group)
- Current full source-backed 245-action decoder is now tested. Real bounded cloud run https://github.com/sstxww/reinforcement-learning/actions/runs/41428807486 **completed success** for source `1eec2a047818b8fea5c7a9c2dd74658cf8856a2a`; model, baseline, SHA/ZIP checks, full match and the bounded concurrency-safe evidence commit all passed.
- Actual V2 model game seed 945077: completed seat-0 placement 8, 122 model actions, 16 final turns, **70 FREEZE (action ID 2), 41 REFRESH (ID 1), 7 END_TURN (ID 0), 1 UPGRADE (ID 3), 1 HERO_POWER (ID 4), 2 CHOOSE (IDs 30 and 32), 0 BUY**. Exactly 37 legal-BUY decision opportunities, zero fallback, zero forced end, simulator guard flags clean. Ten FREEZE actions per controlled turn 1..7; their exact game effects need independent analysis.
- This confirms **excessive repeated FREEZE and refresh plus complete absence of BUY** as observable proximal policy pathology. It does **not** prove WHY model learning produces it, nor that buying on every legal opportunity is economically best.
- Durable report: `reports/s-20261102-9450775f/model-gate.json`; separate honest baseline receipt: `experiments/s-20261102-9450775f/001-945078.json`. No new training steps, no model upgrade. Recovery fingerprint `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- Latest source-head pull-request full-match CI before Actions evidence update: https://github.com/sstxww/reinforcement-learning/actions/runs/41428814101 **success** on `1eec2a047818b8fea5c7a9c2dd74658cf8856a2a`. This research-documentation commit still needs its own current-head CI before merge.
- Prior #41427478915 failed only at final non-fast-forward evidence push; code fix with 3 bounded reapply attempts has now been **genuinely verified** in #41428807486. Artifact copy retained as short-lived fallback, evidence committed in Git.
