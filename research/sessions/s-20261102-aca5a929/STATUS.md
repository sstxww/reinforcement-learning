# Status: s-20261102-aca5a929

- Branch: `agent/s-20261102-aca5a929/optimization-001`, base `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Current state: code+test+bounded push workflow submitted, real execution **pending verification**.
- Research question: public-only card metadata and own-race/pair synergy as a shop-target ranking feature.
- Experiment: 4 configurations × 2 real train seeds, 4 heldout paired seeds, maximum 16 true games; no PPO.
- Current verified match receipts: **none yet in this session**.
- Current verified model/checkpoint: **none yet in this session**.
- Expected output paths: `experiments/s-20261102-aca5a929/`, `reports/s-20261102-aca5a929/001-{weights,results}.json`.
- PR: pending; do not merge or promote without real receipts and latest CI.
- Resume on GitHub branch: `python -m pip install -e '.[test]'; bash scripts/bootstrap_engine.sh; python -m pytest tests/test_card_synergy_aca5a929.py; python -m tavern_ai.card_synergy_aca5a929 --run`.
- Risks: source/observe2 layout drift, engine install, short heldout sample size, weak Baseline. No online ranked play.
