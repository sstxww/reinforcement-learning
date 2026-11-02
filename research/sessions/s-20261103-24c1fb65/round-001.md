# R001 — strict local model-identity binding
- SESSION_ID / TASK_KEY: `s-20261103-24c1fb65` / `eval/active-checkpoint-receipt-sha`
- Base main: `c1b828734527bae6141805581693d890cc3bff94` (do not confuse with later concurrent main)
- Source finding: main's `_verify_full_game_records` checked consistency among receipt hashes but never checked active checkpoint file bytes. This is a **source-level proof of a missing check**, not proof of any historic forged game.
- Hypothesis: a batch of identically mismatched receipts can pass that helper and contaminate paired summaries.
- Minimal fix: digest the selected checkpoint before model runs and again after; reject receipt/checkpoint or checkpoint mid-run mutation. No modifications to training, registry, engines, rewards, or main.
- Regression: consistent wrong model sha, correct mock sha, checkpoint replacement during a mock game; update previous synthetic positive fixture to use real mock-file digest. Must run CI before treating it as verified.
- Environment intended: pinned TavernGym 1.1.0, source hash 6d8712c93022ba11, observe2 4017 float/447 cards, 245 masked actions.
- Actual own training: 0; raw PPO eight-seat game: 0; candidate checkpoint/optimizer/Release: none. Baseline real-game Action is *requested*, not yet completed.
- Handoff: retrieve the actual Action output, verify Game.is_over and eight-seat permutation, commit original receipt; then check complete CI on PR's final SHA and route to sole integrator if no exclusive lease.
