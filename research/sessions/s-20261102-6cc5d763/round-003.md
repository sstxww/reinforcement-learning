# R003: hold R002 policy frozen, extend to 16 unseen paired seeds

- Session `s-20261102-6cc5d763`; branch `agent/s-20261102-6cc5d763/optimization-003`, from verified main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Round 001 PR #27: tested 7 complete matches but zero refresh interventions; no causal comparison.
- Round 002 PR #33: 9 complete matches, 32 interventions across five candidate games; n=4 paired seeds gave mean rank 6.25 vs 7.00 baseline, heavily influenced by one favorable seed. No demonstrated robust improvement.
- R003 hypothesis: this advantage will generalize to 16 **new** paired seeds 36521–36536. Mandatory candidate full game seed 36520, total 33 real matches if completed.
- The policy source `tavern_ai/prebuy_refresh.py` is copied **byte-for-byte** from R002, SHA256 `8af4b69abc82f6c7edc415352f23a73a7a502725cdaa1bbd7129b8b2527fd010`. The extension checks this cryptographically before running.
- Isolated extension implementation `tavern_ai/prebuy_extension.py`, own tests, own bounded Actions workflow `.github/workflows/experiment-s-20261102-6cc5d763-003.yml`.
- TavernGym 1.1.0, source `6d8712c93022ba11`, 4017/447/245, masked actions and native seven bots. Game.is_over and complete receipts required.
- Descriptive metrics plus deterministic 10000-resample paired bootstrap CI for observed rank difference; do not promote Best without robust evidence.
- Strategy evaluation, PPO gradient steps **0**, no new checkpoint, no Arena activity. R001/R002 receipts remain untouched on their branches.
- Execution and statistics: pending at initial commit; data to `experiments/s-20261102-6cc5d763/003-36520.json`, `experiments/s-20261102-6cc5d763/r003-*.json`, `reports/s-20261102-6cc5d763/round-003.json`.
