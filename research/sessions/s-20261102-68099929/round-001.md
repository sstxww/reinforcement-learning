# V5 integration and checkpoint custody — s-20261102-68099929 / R001

## Provenance and integration ownership
- Baseline main at independent branch creation: `3c65ffd0380d6269e6b39c7bf1ca2d84281546d8`.
- Exact branch: `agent/s-20261102-68099929/optimization-001`. Only this branch/session files are written.
- Latest inspected Gmail V5 text instruction on 2026-11-02: prioritize P0 merges, P1 durable resume/evaluation, P2 rank-eight diagnosis before training scale-up.
- **Actual successful integration performed in this session:** PR [#37](https://github.com/sstxww/reinforcement-learning/pull/37) squashed to main at `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`; [post-merge full-game CI 41427071210](https://github.com/sstxww/reinforcement-learning/actions/runs/41427071210) succeeded.
- [PR #25](https://github.com/sstxww/reinforcement-learning/pull/25) was independently integrated by another session first, at `f29a0a6e99161aca4163e51427f6bfabbe02f76f`. This session did **not** claim credit or race a second merge.
- Open PR count at audit snapshot: 68; other sessions continuously change main. Counts are historical snapshots, not a current lock.

## PR integration classification (selected evidence-backed audit)
| Class | PR | Reason and safe action |
| --- | --- | --- |
| A verified engineering | #25, #37 | Both merged; not evidence of competitive strength. |
| B repair / independent CI missing | #8, #9 | #8 conflicts with newer main and latest head lacks CI. #9 has no head-specific PR check; do not merge wholesale. Extract model index from #8 into isolated integration review, preserving provenance. |
| C needs more performance evidence | #24, #35, #73 | Short-runs or weak small-n rule signals; no Champion claim. |
| D negative or no gain | #51, #60, #65, #71, #76, #77 | Retain failures and diagnostics without promoting weaker strategies. #60 depends on #51 and #76 on #72. |
| E duplicate or stacked work | #70 and #75; #51 then #60; #72 then #76 | Source catalogs overlap; compare before combining. Do not merge dependent PR first. |

## P1: tangible selective integration of prior work
- From open draft PR [#8](https://github.com/sstxww/reinforcement-learning/pull/8), selectively copied the conservative `models/registry.json` with source attribution and actual [GitHub Releases API](https://api.github.com/repos/sstxww/reinforcement-learning/releases) inventory of six published prereleases. **Best/Champion remains null.**
- Added `tavern_ai/checkpoint_registry_68099929.py` and regression tests: checks published weight SHA256 against downloaded bytes and metadata, exact TavernGym layout, cumulative training steps, and rejects corrupted archives.
- Created bounded isolated Actions `.github/workflows/release-audit-68099929.yml` to attempt genuine v2 1280-step Release download, hash check, model load, 128-step CPU resume (candidate 1408), and a new genuine baseline full eight-seat canary. Candidate model game is attempted separately and cannot be counted if failed.
- Source v2 Release: `v2-learning-41413557445`, GitHub release asset digest `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, reported total 1280 training steps; prior four held-out ranks all 8 in draft PR #8/#15. Not Champion.
- **Important gate:** Release URL + API digest is *not* a fresh byte-level check. Model download, runtime load, extra PPO steps, own match result and durable candidate publication must be reported only after matching Actions evidence. New 1408-step candidate initially uses a 30-day Artifact, not durable storage, so it cannot be declared saved as a formal model.

## P2: actual poor-model behavior, not a speculative diagnosis
- Draft [PR #60](https://github.com/sstxww/reinforcement-learning/pull/60) reports three completed model-controlled held-out games using a recovered low-LR candidate, ranks [8,8,8], **0 buys in 36 actions** with 21 model-selected EndTurn and no forced end. A 3e-4 reference had [8,8,7], 20 buys across 875 actions, 21 safety-forced ends, and up to 40 identical consecutive actions. Both arms top-four 0%; these numbers are source-PR evidence, not rerun in this session.
- Strong *observation*: premature ending/no purchases in one candidate, repetition in another. Still unproven as causal root: log legal BUY opportunities, gold and shop state; differentiate action mask bug vs preference and paid/zero-cost loop. Do not infer learning-rate causality from 3 seeds.
- Proposed falsifiable next test: compare opportunity-conditioned BUY selection, END_TURN when affordable buy exists, no-state-change transitions and raw-vs-fallback counts at identical held-out seeds/seats. Stop large PPO scale-up until this is measured.

## Actual execution and preservation outcome (updated after successful Actions)

- **Original recovery workflow:** [41427963534](https://github.com/sstxww/reinforcement-learning/actions/runs/41427963534) completed SUCCESS on source HEAD `a7ffcbb566ed9a3e2dc5d1edc59d8021e23d8103`. It ran full repository tests, pinned TavernGym 1.1.0 engine contract, downloaded V2 1280-step Release, verified source SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, loaded actual PPO weights, and **resumed 128 PPO steps** (now 1408). Resumed model SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- The same workflow played two genuine complete games: unpaired baseline seed **99123 rank8**, pure model seed **99124 rank8**, 119 decisions, 15 turns, `Game.is_over()` true, no simulator truncation. Full JSON receipts and source model hash are permanently committed; original resumed ZIP was first in 30-day Artifact (not durable by itself).
- **Candidate custody/paired real games:** [41428692617](https://github.com/sstxww/reinforcement-learning/actions/runs/41428692617) completed SUCCESS. It restored exact SHA256 from prior Artifact, verified load/steps, played independent **3 paired seeds** `[99125,99126,99127]` at seat0 (six actual completed matches). Original baseline ranks **[6,8,8]**, resumed model **[8,8,8]**, mean rank 7.333 vs 8.0; paired challenger-minus-baseline **+0.667** (positive is worse), 0% top4/first, n3 insufficient for strong conclusions. No fallbacks.
- **Durable experiment Release published and independently re-downloaded/verified:**
  [v5-s-20261102-68099929-1408-41428692617](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617).
  GitHub asset: `model.zip`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, 17,525,156 bytes. Includes model metadata, three model-controlled authentic receipts, and paired metrics `reports/s-20261102-68099929/002-paired-custody.json`. The workflow downloaded published ZIP and metadata again and byte-compared. **Challenger only; formal Best/Champion null**. No offsite backup claim.
- Updated branch's `models/registry.json` to **seven** actual Release assets. Latest is the verified 1408-step experimental checkpoint, Best is still null. Existing versions preserved intact. A one-shot guard prevents the original 128-step recovery workflow from repeating due to registry changes.
- **Additional rank-eight diagnosis:** `tavern_ai/buy_opportunity_68099929.py` with regression tests and an isolated genuine-game workflow [41429024658](https://github.com/sstxww/reinforcement-learning/actions/runs/41429024658). Measures `P(BUY|BUY legal)`, END_TURN during legal BUY, distinct legal-shop opportunities, repeated public state hashes; **diagnostic result remains pending until own run completes**, not yet a causal conclusion.
- No Arena ranked play, no prior agent branch alteration, no blind large-scale PPO expansion, no model promotion.
- Next: verify own diagnosis run and source PR-head CI; keep rank-eight root-cause diagnosis separate from storage success.
