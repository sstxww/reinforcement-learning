# V5 R001 — P0 integration inventory and P1/P2 gated recovery

Session: `s-20261102-b71c7aed` · original main HEAD `db5e23ae8c218808821327d806b05d2604cfadfb` · 2026-11-02.

## Real P0 inventory and integration decision

At the live GitHub REST `pulls?state=open&per_page=100` snapshot there were **75 open PRs: 74 Draft**, plus sole non-Draft **#15**, whose base is `agent/learning/v1` from still-Draft **#9** (not main). There was **no immediately safe final-head verified, dependency-free merge** from that snapshot. **No PR was merged by this session.** We did not mark other authors' Drafts ready, cancel their work, or alter main.

Main `db5e23ae8c218808821327d806b05d2604cfadfb` already had successful post-merge full-match CI [#41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040); a concurrent agent had just integrated opt-in HeroPower-Cancel guard in #108, which does not make a PPO policy competitively strong.

| Gate | Representative PRs | Decision |
| --- | --- | --- |
| A: eligible now | none at this snapshot | Do not bypass Draft / explicit author or CI gate |
| B: repair or exact-head retest | #8 (merge conflict), #9 (explicit unmet Release/CI gates), #93 (Draft until final-head CI/concurrent review), #91 (conflict), #84/#86/#95 (Draft with pending gates), #15 (depends on #9) | Keep separate until own-head CI, real receipts, compatibility and owner review |
| C: need replication / more evaluation | #72/#73 (weak uncertain gain), #51 (PPO LR n=6), #103 (evidence useful but source duplicate of integrated diagnostics) | Do not infer strength from small n |
| D: negative / unpromoted experiments | #71 blind-sell worse; #74 card ranker no gain; #61/#65 teacher BC no rank gain; #107 forcing buys still rank 8 | Preserve honest failure knowledge, not weaker policy |
| E: stacked/overlap | #9→#15, #62→#65, #72→#76, #103→#107; card catalogs #67/#68/#75; overlapping Release preflights #82–#95 | Deduplicate against main before any integration |

These groupings are examples, not a claim that every PR is fully source-audited or tested. Never mistake `mergeable: true` or a green older CI for an approved merge.

## Main P1 state and blocker

- Canonical unpromoted registry: `models/registry.json`. `best=null`, `champion=null`; Latest experiment is `v5-s-20261102-68099929-1408-41428692617` (1408 cumulative actual PPO steps) and remains **not promoted**.
- Existing Release `model.zip` expected SHA256: `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Publish/download/hash prior evidence: [Actions 41428692617](https://github.com/sstxww/reinforcement-learning/actions/runs/41428692617). The *newest Release’s own independent optimizer resume* remains a separate gate.
- Shared `.github/workflows/train.yml` restores a previous `v1-model` **Actions Artifact**, which expires, and silently initializes from scratch after download failure; this does not fulfill the V5 requirement for fail-closed durable latest model continuation. Do not modify shared main workflow blindly while other agents integrate.

## P2 — evidence-backed ranked-eighth diagnosis, not an assertion of sole cause

- [Published session s-20261102-68099929 STATUS](../../s-20261102-68099929/STATUS.md) states latest 1408-step candidate ranks `[8,8,8]` vs same-seed baseline `[6,8,8]`, 3 held-out seeds, no gain. n=3 too small to certify magnitude.
- [Actual full game 41429024658](https://github.com/sstxww/reinforcement-learning/actions/runs/41429024658): on seed 99128, raw 1408-step model encountered **35 masked-legal BUY decision exposures across seven turns but made zero purchases**, with 37 REROLL actions and 7 END_TURN actions (zero END_TURN while BUY legal). Baseline had 21 legal BUY exposures and 14 actual BUYs. This proves *legal opportunities existed*; it does **not** prove every individual BUY was optimal or establish reward/embedding causality.
- [s-20261102-83d91476 STATUS](../../s-20261102-83d91476/STATUS.md): V2 two true games rank [8,8], bought zero despite 74 legal BUY exposures; baseline rank [6,7], bought 33/48 exposures. Separate low-LR PR #60 shows a different early-END symptom, not necessarily the same policy failure.
- [s-20261102-ba09e2d4 STATUS](../../s-20261102-ba09e2d4/STATUS.md): disclosed loop guard converted one stalled V2 game to completed eighth place; 0 BUY despite 35/33 legal exposure counts. Engineering completion is not competitive improvement.

**P2 testable hypothesis:** one policy family over-selects REROLL / other actions despite actionable BUY opportunities, while another collapses into END_TURN. Capture unguarded action family *conditioned on legal masks*, compare same-seed actual baseline, then investigate action semantics and feature/reward signals. Do not prematurely generalize across all checkpoints.

## Own isolated P1/P2 execution

- Added `tavern_ai/paired_evidence_b71c7aed.py` reusing already merged `real_trace`, `model_registry.verify_local`, and `registry_integrity.validate_registry`, rather than copying or replacing shared production trainer or registry.
- Added `tests/test_paired_evidence_b71c7aed.py`: 10 locally passed pure invariant checks; guarded, mismatched-SHA, incomplete, duplicate-seed, malformed opportunity and secretly model-backed baseline receipts are rejected.
- Triggered isolated bounded workflow [#41449881452](https://github.com/sstxww/reinforcement-learning/actions/runs/41449881452) on exact code commit `ae9bedf8baba2cc8fe24625297e390a841e8cebb`. It downloads actual two-asset Release, verifies ZIP, metadata, optimizer and CPU load, attempts two genuine same-seed unguarded model/Baseline pairs, then **only after gates** performs a 128-step resume smoke, actual model game, and two held-out comparisons.
- This log is written while run was **in_progress**: no new PPO step, own complete-game receipt or new durable Release is claimed until result is verified. Temporary 30-day Action Artifact is not a durable checkpoint.

## Next gate and handoff

Read actual job logs and artifacts. If failed, preserve exact failure signature; do not fabricate receipts, resume output or model performance. If full match succeeds, copy actual receipt to unique `experiments/s-20261102-b71c7aed/` paths, persist measured summary, and obtain final-head PR CI. Consider main integration only after strict evidence and concurrency review. Do not overwrite Champion (none established), use ranked Arena or widen training without a demonstrated learning signal.

## Verified end-of-round addendum (do not confuse historical pending note)

- **Original run** [41449881452](https://github.com/sstxww/reinforcement-learning/actions/runs/41449881452) failed safely on raw model noncompletion at >250 seat-0 decisions in the same turn; verified weights download, CPU load, pinned engine and 10 own tests passed.
- **Bounded forensic retrial** [41450837403](https://github.com/sstxww/reinforcement-learning/actions/runs/41450837403) independently completed a genuine session-controlled Baseline game seed920021 with 7th place, 16 turns, 71 decisions, 0 truncated combats, 0 engine turn-limit end; original JSON persisted in `experiments/s-20261102-b71c7aed/001-baseline-920021.json`. No candidate model has a new full-game receipt on our heldout seed.
- On seed920011, the 1408-step raw model completed **zero full games** and exhausted a bounded 320 seat-0-action audit on game turn6, including 237 actions in that turn, 32 legal BUY exposures but 0 purchases, and 306 coarse `other` choices. First32 show action1 refresh → action2 freeze repeat, but no full action histogram for all 320; cause remains testable, not proven sole factor. Data is permanently stored in `reports/s-20261102-b71c7aed/001-raw-loop-920011.json` and temporary artifact [13144648818](https://github.com/sstxww/reinforcement-learning/actions/runs/41450837403/artifacts/13144648818).
- **Training budget result:** planned 128 steps were *not run*, because strict raw-game gate failed in both attempts. Net additional actual PPO steps **0**; newly saved weights/Releases **0**; preserved durable 1408-step source Release untouched; Champion/Best null. There is no before/after model improvement or newly completed candidate placement to report.
- **P0 concurrency recheck:** another session merged PR #120 into main during this round at `a29e36e20e59b9790e0842b388336a141df9c65d`. This session **did not merge it** or overwrite main. Other fresh non-Draft PR #114 reverted to Draft while we were checking, and #15 is still stacked on Draft #9. The opening 75-PR table is a time-stamped snapshot, not current ongoing count.
- **Iteration diagnosis and bounded action:** preserve fail-closed evaluator and legal-mask telemetry, stop repeating the same failing raw model/seed, and test a new single-variable policy hypothesis in a separate, truly isolated round (e.g., classify full action 1/2 histogram and public shop state changes before changing reward or forcing BUY). Prior PR #107 indicates forcing more buys did not establish rank gain. Do not start more blind PPO on this checkpoint.
