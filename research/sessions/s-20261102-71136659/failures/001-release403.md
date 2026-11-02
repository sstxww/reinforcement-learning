# R001 publication failure — confirmed permission error

- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41449601213
- Job: `verify-resume`, ID `125291232638`.
- First failing step: `Publish only validated, unpromoted, durable candidate`.
- Command: `gh release create v5-smoke-s-20261102-71136659-r001 ... outputs/model.zip outputs/model.metadata.json ...`.
- Exact failure: `HTTP 403: Resource not accessible by integration (https://api.github.com/repos/sstxww/reinforcement-learning/releases)`.
- Prior steps: **successful** pinned engine, 7/7 unit tests, SHA-verified source download, 1408→1536 PPO continuation and both genuine seed 99373 eight-seat games.
- New model SHA256: `8ab19be62d6f43bce92148c08cb975d355f506fab821b77ed96c2b748705e588`.
- Temporary fallback: https://github.com/sstxww/reinforcement-learning/actions/runs/41449601213/artifacts/13143508961, 30 days. **NOT durable storage**; no claimed Release.
- Root category: GitHub integration lacks effective Release write authorization in this job despite YAML `contents: write`. Exact policy cause not proven.
- Safe response: do not rerun same 403 repeatedly; do not print tokens or upload weights to Git history. Preserve receipts, metadata, hashes and logs. Authorized maintainer/publisher must resolve permission / use durable storage, then verify resulting Release hash, download, load, optimizer resume and true match.
- No Champion promotion, no model-performance success claim: candidate seed 99373 rank 8 vs baseline rank 5; n=1.
