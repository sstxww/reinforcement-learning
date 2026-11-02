# Failure 001: observe2 card length ≠ legacy layout()

- Session: `s-20261102-aca5a929`, Round 001.
- First attempt: [GitHub Actions 41421892518](https://github.com/sstxww/reinforcement-learning/actions/runs/41421892518), head `9e11a44cf591dd3cb511c44e7de16c61f9f50c18`: **failure**.
- Environment: TavernGym 1.1.0, source `6d8712c93022ba11`; engine built, pinned patch checksum passed and 11 isolated unit tests passed.
- Exact failure: `ValueError: Incorrect observe2 input shape` in `tavern_ai/card_synergy_aca5a929.py:best_buy`, at the first attempted real-game buy action. No completed game was produced in this run.
- Root cause: `Game.observe2` produces 447 card IDs, but upstream `taverngym.layout()["OBS_CARDS"]` describes 124 older `Game.observe` slots. The old layout has historical board/hand/shop offsets, and cannot be used as the full observe2 tensor length.
- Repair 1 commit: `2fd46064290c772e79318fbe75c442ff31851506`; use the pinned public `CARDS=447` contract for Arena observation length. Before full training, instantiate a real engine Game and explicitly verify that the old board/hand/shop card-index prefix is preserved by observe2. If not, refuse further training rather than silently read incorrect card IDs.
- Repair-run: [GitHub Actions 41422373796](https://github.com/sstxww/reinforcement-learning/actions/runs/41422373796). Status and outcome to be added from observed logs.
- Bounded retries: initial execution + at most 2 meaningful fixes; never re-run the same deterministic broken SHA.


## Verified repair outcome
- [Actions 41422373796](https://github.com/sstxww/reinforcement-learning/actions/runs/41422373796) **SUCCESS** after fix: pinned engine hash checked, real old observe/card stream compared with extended observe2, all 16 actual full-game receipts completed and validated.
- Additional regression `tests/test_obs2_bridge_s20261102_aca5a929.py` covers public-card prefix on a real installed engine (skipped if the engine is absent). The executable training path independently asserts this compatibility before any optimization.
- No second repair needed. One initial failure, one substantial repair, one successful retest. The false shape guard caused no invalid game results or leaked model promotion.
