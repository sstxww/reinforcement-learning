# s-20261102-68099929 — V5 live status (2026-11-02)

## Completed and independently verifiable
- Integration ownership: **PR #37** was merged by this session to main at `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`; actual post-merge full-game CI run **41427071210 SUCCESS**.
- PR #25 was merged by *another* session at `f29a0a6e99161aca4163e51427f6bfabbe02f76f` while we were inspecting; we did not duplicate its merge.
- Six existing experimental model Releases are indexed in this branch's `models/registry.json`, selectively extracted from #8; formal Champion/Best remains null.
- **True executable Actions run [41427963534](https://github.com/sstxww/reinforcement-learning/actions/runs/41427963534): SUCCESS.** Tests and pinned TavernGym engine succeeded. Actual V2 source Release 1280-step ZIP downloaded and SHA256 verified: `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- Actual source model loaded and **128 additional PPO steps** performed, 1280→**1408 cumulative steps**. Actual resumed model SHA256: `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Code SHA for run: `a7ffcbb566ed9a3e2dc5d1edc59d8021e23d8103`.
- **Two real complete independent eight-seat games** in run: baseline seed 99123 placement **8**, model-controlled pure (no fallback guard) seed 99124 placement **8**, 119 model decisions, 15 turns, `Game.is_over` and no combat truncation. These are different seeds, **not a paired rank comparison**.
- Real evidence committed on own branch `d597a4487966f598347a9a31185357bd7f51f22f`: `reports/s-20261102-68099929/001-release-audit.json` plus two genuine game receipts. Model ZIP retained in **30-day Actions Artifact 13132962785**, expires 2026-12-02; **not yet durable long-term**.

## Still running / gates not claimed
- Candidate custody and 3-seed genuine same-seed baseline/model comparisons: [Actions 41428692617](https://github.com/sstxww/reinforcement-learning/actions/runs/41428692617). Will attempt immutable prerelease publication/download verification **only after paired real full games**. No publication claimed until success and Release URL returned.
- Opportunity-conditioned model-vs-baseline legal BUY telemetry: [Actions 41429024658](https://github.com/sstxww/reinforcement-learning/actions/runs/41429024658). Actual model BUY vs mask opportunity remains unknown until this completes.
- Latest PR-head CI not yet verified for new integration branch. No Champion promotion, no large-scale PPO expansion; 1408-step candidate was a recovery smoke test and ranked 8.
- Single-branch integration scope: `agent/s-20261102-68099929/optimization-001`, base main at creation `3c65ffd0380d6269e6b39c7bf1ca2d84281546d8`.
