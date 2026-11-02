# 001 — historical V2 metadata schema mismatch

- First actual run: https://github.com/sstxww/reinforcement-learning/actions/runs/41427542987
- Failure signature: `ValueError: Invalid checkpoint metadata schema` in model registry preflight.
- Real trigger: V2 Release `model.metadata.json` uses schema 2, with nested compatibility and checkpoint SHA. Main's V1 trainer emits schema 1. Initial validator only accepted schema 1; this was an audit bug rather than an invalid model.
- Fix: commit `94723a15e3ba9a8f5f36d721668e21d1487629aa` supports both schemas while checking V2 compatibility and claimed SHA; includes synthetic schema2 tampering regression.
- Verified retest: https://github.com/sstxww/reinforcement-learning/actions/runs/41428441545 **SUCCESS**, ZIP CRC, optimizer, CPU load, 128-step resume, model games and paired evaluation.
- No fabricated receipts, no hidden fallback, and no claim of competitive gain.
