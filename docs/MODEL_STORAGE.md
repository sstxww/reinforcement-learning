# Model storage and recovery policy

Training artifacts expire; they are **not** the long-term checkpoint database. The modified main training workflow, once merged and verified, publishes candidate model snapshots to versioned prerelease tags `v1-main-<workflow-run-id>` in **this repository's GitHub Releases**. Each Release is expected to include `model.zip` (network weights **and optimizer state**), `model.metadata.json`, `model.sha256`, a genuine model-game receipt, and seeded evaluation metrics.

The branch-local learning experiment may publish a separate `v1-learning-<source-sha>` candidate prerelease. A release workflow configuration is **not proof** that a Release already exists. Verify an actual Release asset and hash before claiming permanent recoverability.

## Recovery procedure (GitHub runner)

Find the newest validated compatible candidate in GitHub Releases. Download `model.zip` and `model.metadata.json` to `checkpoints/` and inspect `model.sha256` if provided. Check the upstream commit, engine source hash, catalog checksum, ruleset, patch checksum and observation shape against `tavern_ai/contract.py`. The training CLI rejects incompatible resumed checkpoints; a missing or incompatible model should fail closed rather than be promoted.

A verified example invocation is defined by the code and environment:

```bash
python -m tavern_ai.train --steps 2048 --seed 42 --resume checkpoints/model.zip --out checkpoints/model.zip
```

Set `best` in `models/registry.json` **only after independent paired-seed evaluation**. `latest` is for continuation, not evidence of a stronger policy. Never overwrite validated best or delete an older candidate without loading and testing the kept checkpoint. No permanent checkpoint should be claimed until a Release has actually been created and its assets successfully checked.

At this stage, `models/registry.json` intentionally uses `null` for best and latest. It must be updated only after actual validation and through a reviewed PR.
