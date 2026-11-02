# s-20261102-661adf61 STATUS — round 001 real execution complete

- Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Branch: `agent/s-20261102-661adf61/optimization-001`
- Experiment execution SHA: `3e093f073f8f461725ce2cff20edb98e600f9179`
- [Real GitHub Actions run 41419937945](https://github.com/sstxww/reinforcement-learning/actions/runs/41419937945): **completed success**
- Training: 80 supervised updates on 128 teacher states, 0 PPO steps
- Reproducible real match evidence: `experiments/s-20261102-661adf61/001-*.json` (8 full matches); combined `reports/s-20261102-661adf61/001-masked-bc.json`
- Best tested candidate: **none promoted**; BC raw n=1 rank 7, teacher n=2 mean 7.5, guarded BC n=2 mean 7.0 with 0 forced ends
- SHA256: `b77aab475a502dacd2c036f4df87cbadd4656299bf5baaa13f16569b04699cd8`
- Checkpoint: GitHub Actions artifact #13128524452, named `bc-session-s-20261102-661adf61`, 30-day retention, expires 2026-12-02 09:24:05 UTC; NOT permanently persisted or release-restored
- Recommendation: **RETEST**, n=2 is insufficient to support promotion
- PR/CI: pending creation and independent gate validation; do not treat custom workflow success as PR CI
- Restoration: download artifact from run above before expiry, verify SHA256 of `bc-model.pt`, verify TavernGym source fingerprint, then rerun held-out game evaluation. Full reproduction via `python -m tavern_ai.bc_session_661adf61 --updates 80 --outdir experiments/s-20261102-661adf61`.
- Next: more raw held-out seeds and action-band telemetry to diagnose rank 7–8 weakness; no Arena play
