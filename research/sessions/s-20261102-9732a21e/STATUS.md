# V5 Agent s-20261102-9732a21e — verified integration, model recovery and behavioral diagnosis

## GitHub integration
- Authored session branch: `agent/s-20261102-9732a21e/optimization-001`. Sole writable repository `sstxww/reinforcement-learning`; no TavernArena ranked.
- **Our merged PR #70** engine card/action contract audit: commit `3c65ffd0380d6269e6b39c7bf1ca2d84281546d8`, post-merge [CI 41427295858](https://github.com/sstxww/reinforcement-learning/actions/runs/41427295858) success.
- **PR #25** strict receipt integrity merged by a parallel session (not credited as our action). PR #75 overlapping schema received deduplication comment, no blind merge.
- **Our active Draft PR #86:** https://github.com/sstxww/reinforcement-learning/pull/86. Local final-head CI must be checked after all changes.

## R001 completed training, failed paired evaluation
- [Actions 41427627265](https://github.com/sstxww/reinforcement-learning/actions/runs/41427627265) failed at pure-model heldout `Full-game safety limit exceeded`, **not** at Release restore, SHA validation, or actual PPO training.
- V2 Release source 1280 PPO steps -> verified **1408** saved steps (+128), original first candidate SHA256 `04799f7e23153dd1728d6e765386ea5f9c17da4075ec7672d17cf4dfb170e185`.
- Original unchanged artifact game receipt seed 83601 (rank 8, 15 turns, 117 decisions, valid eight placements) committed at `experiments/s-20261102-9732a21e/001-83601.json`; artifact 13132927436 archived 30 days. Original failed paired run gives **zero complete paired comparisons**. See failure report `failures/001-eval-fullgame-safety-limit.md`.

## R002 successful recovery, permanent rejected checkpoint and direct root cause
- [Actions 41428791989](https://github.com/sstxww/reinforcement-learning/actions/runs/41428791989) **completed SUCCESS**. Repeat bounded 128-step restore from original 1280-step V2 release to 1408 steps. Source Release model SHA and engine contract validated; candidate alone completed seed 83601 rank 8.
- **Durable unpromoted model Release**: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-resume-smoke-s-20261102-9732a21e-r001
- Candidate weight SHA256 `976d9323e79cd00fa1dae73ea31886e4087171078eabdde8eeca06fac7eb0cc6`; metadata SHA256 `83d4a7d5df6d18b9fcc4816edd14988ab2f4e5768cdd41fa2f670cf2b6df7991`. Release roundtrip check and manifest roundtrip check **passed**. `reports/s-20261102-9732a21e/001-model-lineage.json` contains `checkpoint_persistence=verified_release_roundtrip`, `model_status=rejected_behavior_safety_failure`, `formal_resume_allowed=false`; do **NOT** promote Champion/Latest/Best or use this unsafe model as formal continuation base.
- Public-observation diagnostic `reports/s-20261102-9732a21e/001-behavior-telemetry.json` confirms:
  - Seed 83701: pure candidate **failed** to complete at turn 6, 30,000 decisions; `Play=14955`, `Cancel=14955`, 50 `Freeze`, 32 `Refresh`; **86 decision points with some legal buy**, **0 buys**. This failed game has **no rank**. Official rule baseline on same seed completed rank 8 with 13 buys.
  - Seed 83702: pure candidate completed **rank 8**, 122 decisions, 70 Freeze / 42 Refresh / 7 EndTurn / 1 Upgrade / 2 Choose; **39 decision points with legal buy**, **0 buys**. Official baseline same seed completed rank 8 with 10 buys.
  - **Total 125 model decisions with some legal purchase**, **zero buys**, but these counts include repeated choices in the stuck loop and are not 125 independent economic opportunities. Full-game failure explains unsafe model. **Only 1/2 paired seeds completed**; both models rank 8 on that seed. No strength uplift.
- Root cause level: **observed action behavior failure** (buy-action omission, Play/Cancel loop, Freeze/Refresh spam); not yet causal proof of reward or learning-rate mechanism. Probe captures only public obs2 and legal mask; no hidden-information leak.

## R003 isolated behavior intervention
- One-factor legal-action hybrid (maximum 2 buying overrides per turn; only mask-legal END_TURN after 35 actions/turn), explicitly **not pure PPO**. New source `tavern_ai/v5_guarded_9732a21e.py`, tests, branch-specific workflow. It reuses the *rejected* checkpoint only as a fixed research model; zero new training steps.
- 4-seed pilot, 8 real games planned; no results yet. [Actions 41429774484](https://github.com/sstxww/reinforcement-learning/actions/runs/41429774484) **queued at this edit**. All complete hybrid receipts are labelled `policy=guarded_model_diagnostic` and kept under reports, never claimed as native PPO victories. Incomplete games get only diagnostics.
- No large PPO scale-up until actual behavior gate / valid paired samples show improvement.
