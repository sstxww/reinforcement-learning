# Round 002 incident — mixed legacy and observe2 layout

- Failure type: environment contract mismatch at real-game launch; **no game receipts produced on this run**.
- Failed workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41416920871
- Source SHA: 94876668301772a9ae80914ab660edb4155c209a; job ID 125182928363; seeds planned 29201–29210, no seed executed.
- Unit tests and pinned real engine installation passed.
- Exact exception: `RuntimeError: Unexpected upstream layout` from `freeze_value_s_717d0e50.py:132`.
- Actual `taverngym.layout()` returns both legacy `OBS_FLOATS=3227, OBS_CARDS=124` and patched `OBS2_FLOATS=4017, OBS2_CARDS=447`; `N_ACTIONS=245`. Previous guard incorrectly compared legacy sizes to observe2.
- Secondary correctness risk located by source review: the end-turn shop-value heuristic used legacy offsets but incorrectly passed the 4017-vector. Merely changing the guard to OBS2 would silently read unrelated float slots.
- Reproduction: run original source with pinned TavernGym 1.1.0, source hash `6d8712c93022ba11`, then `python -m tavern_ai.freeze_value_s_717d0e50`.
- Root-cause fix: verify both contracts, continue verifying observe2 4017/447 on each candidate decision, read the **same player's public legacy Game.observe(0)** only to decode shop slots via the documented legacy offsets. No hidden opponent data. Validate its 3227-length and finite values before deciding.
- New regression: test both legacy and V2 dimension constants; assert shop offset 685 and reject either mismatch.
- Rerun: pending after submitting this fix. No existing CI run or non-existent match receipt is represented as a success.
