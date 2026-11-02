# Session status — s-20261102-d97f219e

- State: `running_real_engine_audit` (not a model-strength claim)
- Branch: `agent/s-20261102-d97f219e/optimization-001`
- Base main commit: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- PR: pending until real run and receipt inspection
- Hypothesis: same TavernGym seed must replay the exact seat-0 action/observation trajectory when the order of other seeded games is reversed
- Active code: `tavern_ai/replay_audit_d97f219e.py` and its unit tests
- Isolated Action: `.github/workflows/replay-audit-d97f219e.yml`
- Run: inspect workflow after first branch push; do not assume success
- PPO steps: **0** (pure reproducibility engineering experiment)
- Latest / candidate / best model: no models produced, no checkpoint to restore
- Planned receipt: `experiments/s-20261102-d97f219e/001-36011.json`
- Planned metrics: `reports/s-20261102-d97f219e/replay-001.json`
- Next: audit actual Actions run, trace mismatches if any, independently evaluate, update report, request review
