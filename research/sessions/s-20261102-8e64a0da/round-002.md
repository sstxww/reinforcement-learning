# s-20261102-8e64a0da R002: true same-seed heldout diagnostics after verified 1408→1536 PPO resume

## Actual motivating evidence
Own [GitHub Actions 41450146951](https://github.com/sstxww/reinforcement-learning/actions/runs/41450146951) SUCCESS: original V5 experimental 1408-step published Release was independently downloaded and verified, 128 real PPO steps restored existing optimizer (Adam 88→96), producing cumulative 1536 steps. New checkpoint SHA c3bc7cd952bbf02fb4a15e3866a13c98bc9f1486eb3de35fd119b1651f81a73a was published as [experimental Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-smoke-s-20261102-8e64a0da-resume128) and redownload verified. The resumed model finished one unguarded true eight-seat TavernGym game seed 90312, rank 8. Own baseline seed 90311 rank 8 but **not matched seed**.

## Single R002 question
Does the actual saved 1408→1536 PPO continuation alter raw model behavior or placement on new **identical seed, same seat** heldout games? Compare 1408 vs 1536 vs rules baseline, all real TavernGym, with per-game truthful receipt and action-family metrics. This is evaluation not extra training.

## True-game constraints
- Use TavernGym 1.1.0 source fingerprint 6d8712c93022ba11, no Arena, no hidden opponent input, no invented complete games.
- Restore exact two published immutable model weights and metadata, verify hashes and CPU load; no use of transient artifact as canonical model.
- Run **two** fresh matched heldout seed triples 90321 and 90322; seat0 for all arms; no fallback, forced EndTurn, shop-purchase override, champion promotion, or unsourced rank claims.
- Use already integrated main `tavern_ai.behavior_probe_ba09e2d4` to trace real mask-legal BUY opportunities and HeroPower/Cancel/Refresh/Freeze action counts; explicitly archive unfinished raw model probes without fake receipts.
- Save independent authentic receipt for baseline seeds, raw-model receipts only if full game completed with `Game.is_over()`. Summarize paired rank only for complete triples, report insufficiency honestly.
- Dedicated branch-only bounded Actions, 0 additional PPO training steps in this round; no writes to shared trainer, evaluator, central registry or other sessions.

P0 integration remains independent (#102 already main). R001 PR #146 is a separate draft and this R002 does not require merging it; it uses its already published versioned Release.

## Evidence status
At workflow creation, new R002 paired game count = 0; must check own Actions results and generated reports, and update this note before any performance conclusions.
