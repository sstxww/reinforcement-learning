# Round 001 — s-20261103-db1986b8

## P0 live review and integration decisions
Initial main `9685cc33c0f05821de3e0a8d2997aedeb3725500`; main full-game CI 41506832439 SUCCESS. 115 open PRs, 114 Draft. #15 explicitly depends on Draft #9. Existing PRs #128/#132/#134/#149 alter shared train.yml, #142/#147/#151 propose Release gateways, #144/#145/#148/#155/#156 overlap model evidence. Avoid duplicate main merges; this session merged none. Read AGENTS.md, README, background/session/failure protocols, main train/evaluate/registry, release evidence, and PR diffs.

## Concrete P1 commits
- `tavern_ai/main_resume_source_db1986b8.py`: fail-closed registered durable Release selection.
- `tests/test_main_resume_source_db1986b8.py` and `tests/test_main_v5_workflow_db1986b8.py`: synthetic/offline integrity checks (not game data).
- `.github/workflows/train.yml` on isolated branch: eliminates missing Artifact→silent random reset; download canonical Release + verify registered SHA256, ZIP/engine/CPU inference; bounded 128–512 genuine PPO steps to independent candidate path; raw candidate game; paired heldout old/new/Baseline; publish **unpromoted** GitHub Release only after full success, redownload+compare, no Champion. Disable automatic weekly runs while rank-8 raw gate remains suspect.
- Unique `.github/workflows/v5-integration-s-20261103-db1986b8.yml`: pinned-engine unit + authentic own baseline smoke.

## Authentic executed evidence
[Run 41507827256](https://github.com/sstxww/reinforcement-learning/actions/runs/41507827256): SUCCESS (unit suite, source-pinned TavernGym 1.1.0 observe2 4017 features/447 card slots/245 actions, original baseline full game). Artifact 13172960456 was downloaded and its `001-931281.json` inspected. SHA256 `ff9c0c8489884955d59a54874c6fa8f596551a410780cf6630e3714d7c64133d`, policy baseline, agent s-20261103-db1986b8, seed 931281, placements [6,5,7,1,3,2,8,4], own rank 6, 55 decisions, 15 turns, complete, 0 combat truncations. This is not PPO strength evidence.

## P2 why rank-eight (observed, not sole cause)
- PR #103: real V2 guarded games reported no buys in many legal-buy opportunities, rank 8. 
- PR #107: 46 forced legal Buys over 3 actual guarded games still [8,8,8] with many Play/Cancel cycles; purchase alone insufficient.
- PR #156: raw V5 inference repeatedly REFRESH/FREEZE with legal BUY opportunities; 320 actions before completing a raw game, so NOT valid full-game rank evidence.
Hypotheses to test: action mask/semantic encoding, choice resolution, value/entropy collapse, reward and observation transfer, public-state delta per move. Do not blame only training size or promote failed candidates.

## Training and storage handoff
Registry latest unpromoted V5 1408 steps, SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632, heldout [8,8,8], baseline [6,8,8], no Champion. Own new training **0 steps**, own model games **0**, saved new weights **0**. This P1 workflow has not been run end-to-end: requires independent registered Release roundtrip, current-main PR CI, raw model game and archive check before merge. Current `tavern_ai.train.run` downgrades schema-2 metadata; registry won't auto-advance latest after Release. No unsupported success claims, no ranked Arena. Need coordinate conflicts with multiple parallel agents.
