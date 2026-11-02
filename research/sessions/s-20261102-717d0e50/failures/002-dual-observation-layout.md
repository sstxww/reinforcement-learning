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
- First repair run https://github.com/sstxww/reinforcement-learning/actions/runs/41417550965 failed in the newly added `test_dual_observation_contract_and_shop_offsets` before engine bootstrap: expected real shop start 685, received 488 because the old unit-test fixture intentionally used fake GLOBAL_F=60/MINION_F=19/ITEM_F=28. This was a **fixture error**, not simulator behavior, and still produced zero match receipts.
- Second root-cause fix: override only the dual-version contract test fixture with the real values GLOBAL_F=53, MINION_F=31, ITEM_F=40; keep the older synthetic behavior tests unchanged.
- Final retest: https://github.com/sstxww/reinforcement-learning/actions/runs/41417682184 succeeded at fixed SHA 5610b37eec2f0fa3b2926bdc5b49b232ce9c5dac (all unit tests, genuine TavernGym install, **30 completed eight-player games**, all receipt checks, evidence persistence). No false success claims from either failed run. Two meaningful fixes addressed distinct error signatures.
