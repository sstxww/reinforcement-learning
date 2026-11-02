# 001 — Genuine raw model game did not terminate (seed 931282)

Source run: https://github.com/sstxww/reinforcement-learning/actions/runs/41509839883

Real registered V2 parent `v2-learning-41413557445`, 1280 steps, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. Actual +128 PPO optimizer steps produced schema-2 1408-step child SHA256 `f488738b738708380f3d4bc2e607843f8f2931b4aac3883d775c5d9ae090d762`, with correct source lineage, CPU inference and strict ZIP integrity.

Raw game command:
`python -m tavern_ai.canary --agent-id s-20261103-db1986b8 --seed 931282 --policy model --model checkpoints/schema2-child.zip --receipt outputs/001-raw-model-931282.json`

Actual `outputs/raw-model-status.json`: `{"attempted":true,"exit_code":1,"full_game_completed":false,"may_be_timeout":false}`. Real stack trace from `tavern_ai/canary.py` loop: `RuntimeError: Full-game safety limit exceeded`. The 30,000-iteration runner ceiling was reached; no full game receipt was created or committed and **no rank** is recorded. This is NOT a completed eighth place finish. There was no guard or fallback substituted.

Genuine source logs, raw model failure and SHA-bound child weights were saved with [REJECTED Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-rejected-s-20261103-db1986b8-schema2-1408-41509839883), publication run 41510761629 (byte-verified). Candidate was **not** promoted to Latest/Best/Champion and is not permitted as an automatic continuation source.

Likely investigation: track public turn/phase state deltas and legal action opportunities; identify REFRESH/FREEZE/HERO/CANCEL repeated sequences and where END_TURN progress is inhibited. Other evidence #162 / #107 supports recurrent purchase and action-progress issues, but this single trace does not prove one root cause. Test against original raw complete games and matched baseline after fixing, not synthetic rank claims.
