# Status: s-20261102-aca5a929

- Branch: `agent/s-20261102-aca5a929/optimization-001`; base `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Current state: **experiment complete, REJECT as competitive upgrade**, PR review pending. No main/upstream/Champion writes.
- Verified [training+heldout full-engine Actions #41422373796](https://github.com/sstxww/reinforcement-learning/actions/runs/41422373796): SUCCESS, all 16 genuine completed eight-seat games and checkpoint SHA256 validated.
- Earlier [failed run #41421892518](https://github.com/sstxww/reinforcement-learning/actions/runs/41421892518) isolated old-vs-observe2 card length bug; [fix `2fd4606`](https://github.com/sstxww/reinforcement-learning/commit/2fd46064290c772e79318fbe75c442ff31851506) verified in success run.
- Training: 4 parameter choices × 2 seeds 79110/79111 = 8 real games; no PPO/gradient steps. Frozen chosen `stat=1,tier=0.5,race=0,pair=0`.
- Heldout: seeds 79220–79223, candidate `[8,8,7,6]`, baseline `[6,8,8,7]`, both mean 7.25, top4 0%, first 0%; no demonstrated gain. Candidate buy choice overrides 31, guard triggers 0.
- Checkpoint: `reports/s-20261102-aca5a929/001-weights.json`; SHA256 `971acb6755401e700b26caf251d390903df4fbb67cf1b6015e956b270439bcc4` (small param JSON, not neural weights).
- Report: `reports/s-20261102-aca5a929/001-results.json`; receipts: `experiments/s-20261102-aca5a929/*.json` (16 records).
- Rules pinned: TavernGym 1.1.0, source `6d8712c93022ba11`, observe2 4017/447/245.
- Regression: `tests/test_obs2_bridge_s20261102_aca5a929.py` + live runtime prefix assertion; no hidden data used.
- PR: draft for review after receipts; see GitHub PR associated with this branch.
- Resume: `python -m pip install -e '.[test]'; bash scripts/bootstrap_engine.sh; python -m pytest; python -m tavern_ai.card_synergy_aca5a929 --run`. Repeat uses same train/test seeds; do not confuse reproducibility with an independent new sample.
- Latest integration advice: preserve negative finding and observe2 regression; do not merge as a stronger model or declare Champion. New hypothesis: supervised tactical shop-card evaluation conditioned on phase and board combat need instead of static tribe counts.
