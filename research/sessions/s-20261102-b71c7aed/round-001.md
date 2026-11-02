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
