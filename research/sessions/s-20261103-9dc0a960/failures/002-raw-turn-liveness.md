# R001: raw MaskablePPO cannot complete due to own-turn liveness budget

- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41510804758
- Job: https://github.com/sstxww/reinforcement-learning/actions/runs/41510804758/job/125501843601
- Source branch HEAD: `36e01edf6910b3bde5f82841477ba3ec90c97fdc`.
- Model: unpromoted 1408-step GitHub Release `v5-s-20261102-68099929-1408-41428692617`, verified ZIP SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- Pinned TavernGym version 1.1.0 / source_hash `6d8712c93022ba11`. Seed 43837, controlled seat 0, deterministic unassisted raw model, no fallback.
- `failure_signature`: `raw_model_turn_liveness_budget`. After 223 raw own decisions, turn 7 reached 120 own decisions in that turn, and game was NOT over. Exit code 3 is intended fail-closed behavior; no placement and no completed-game model receipt.
- Measured 88 decision exposures with at least one mask-legal BUY ID 8..15, zero chosen BUY; action IDs histogram 1:31, 2:60, 7:60, 46:61, 0:6, 3:1, 31:1, 32:3. The action+public observation hash changed across consecutive own-seat decisions; unchanged digest count zero is not proof of meaningful economic progress. No independent gold/affordability inference is made.
- Verified scripted baseline independently completed a real 8-seat game on the same seed with placements `[8,2,5,7,3,6,4,1]`; this is not evidence the raw model finished or that the baseline is strong.
- [Full diagnostics artifact (30-day retention)](https://github.com/sstxww/reinforcement-learning/actions/runs/41510804758/artifacts/13172359996), full JSON digest `69327fc4b3d939b1137da301c4cef2f37a9820afcbf7988f40bbdcd8c29ef939`, ZIP digest `5028ef418ddb4ed9a333dcc82f26eb23c2ea7395ea808309c1da140a65a2ce89`. Concise durable summary: `reports/s-20261103-9dc0a960/raw-ppo-43837-summary.json`.
- Root cause: **observable model economic/liveness malfunction**; exact underlying cause among policy logits, raw ID semantics, mask, reward, data mismatch remains **unproven**. Focused tests, engine bootstrap, baseline, and model download all succeeded, so that prior test schema failure has been fixed.
- Repeat policy: do NOT restart identical model SHA/seed/guard-free decision trace. Next reproducible change should verify ID-to-semantics and masked logits, then run fresh seed(s) with a genuinely modified hypothesis.
- Classification: `blocked_with_evidence`; true new PPO training steps = 0; model strength assessment cannot compute paired placements, no model Release or promotion.
