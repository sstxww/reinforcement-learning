# s-20261102-68099929 — V5 verified final evidence state

## Integrated to main by this session
- PR #37: deterministic seeded confidence/paired comparisons, merged commit `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`. Exact post-merge full-match CI [41427071210](https://github.com/sstxww/reinforcement-learning/actions/runs/41427071210): SUCCESS.
- PR #25 was merged by another independent session during audit; no duplicate merge or overwrite by this session.

## Real model restoration, resumed training, reliable saved candidate
- Source: [V2 original 1280-step Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445), SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- [Run 41427963534](https://github.com/sstxww/reinforcement-learning/actions/runs/41427963534) SUCCESS: downloaded bytes+metadata verified, true MaskablePPO load, 128 real additional steps to **1408**, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Real baseline seed99123 rank8; genuine model seed99124 rank8, 119 decisions, no fallback/engine truncation.
- [Run 41428692617](https://github.com/sstxww/reinforcement-learning/actions/runs/41428692617) SUCCESS: three completed paired seed games each arm (99125–99127); rule baseline ranks **[6,8,8]**, 1408-step PPO **[8,8,8]**; model mean8 vs baseline7.333. No gain, n3 only.
- **Published & independently redownloaded valid GitHub Release**: [v5-s-20261102-68099929-1408-41428692617](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617). ZIP and metadata checked exactly; 7 Releases indexed in `models/registry.json`, older versions preserved. Newest verified Challenger; **Best/Champion remains null**.

## Rank-eight diagnosis — actual observed public legal opportunities
- [Run 41429024658](https://github.com/sstxww/reinforcement-learning/actions/runs/41429024658) SUCCESS: genuine paired seed99128, baseline/model both rank8; model **35 legal masked BUY decisions across 7 distinct turns**, **0 buys**, **37 rerolls**, **70 other actions**, 7 END_TURN (none when BUY legal), zero forced ends and zero identical consecutive public observations. Baseline had 21 legal BUY opportunities, chose 14 buys. This demonstrates the model skipped real legal BUY actions; no proven sole causal root or strength gain.
- Evidence: `experiments/s-20261102-68099929/003-{baseline,model}-99128.json` and `reports/s-20261102-68099929/003-buy-opportunity.json`; other true receipts and model hashes in `001-` and `002-` batches.
- Separate source PR #60 diagnoses different low-LR models (early END_TURN vs repeated actions); do not falsely equate those checkpoints with this 1408-step model.

## Own PR and CI gate
- Integration PR [#106](https://github.com/sstxww/reinforcement-learning/pull/106) contains toolchain, registry, studies, owned reports and **10 genuine full-game receipts**; originally conflicted with concurrent main registry, resolved by main+session two-parent merge commit `2a326f147f662c4e096a1be5b57ec3782cc99b53` without removing main-only assets.
- A temporary branch-only one-shot workflow YAML parser failure occurred after original successful training; see `failures/002-one-shot-workflow-yaml.md`. Fixed so no duplicate PPO job executes. It is NOT a failed PPO training attempt.
- PR remains Draft until exact final-head CI full-eight-seat check passes. No ranked TavernArena, no upstream writes, no Champion promotion, no scale-up of unproven PPO.
- Base main at own branch creation: `3c65ffd0380d6269e6b39c7bf1ca2d84281546d8`.
