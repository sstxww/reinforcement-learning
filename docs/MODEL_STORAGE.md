# Model storage, lifecycle and recovery

## Confirmed real candidate (November 2, 2026)

The independent learning experiment completed **256 actual MaskablePPO steps** and a genuine full TavernGym model game (seed 1302, rank 8). Three held-out model matches (seeds 24000–24002) all ranked 8. These are **poor results**, not evidence of improvement.

A durable prerelease checkpoint exists in **this repository only**:

- Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v1-learning-9eada5801f99
- Model asset: `model.zip`, SHA-256 `dc5195658995358e70c0d565a979b9cf05ccc5e47ae7adaa0a2f078f01cad917`
- Companion `model.metadata.json` contains strict engine/catalog/patch/upstream compatibility metadata, training seed and step count.
- Real receipts: `experiments/learning/v1-model-match.json`, `reports/learning/v1-heldout.json`.
- Source Actions: https://github.com/sstxww/reinforcement-learning/actions/runs/41412362662

A prior model in run 41412048034 failed the game safety limit. Its separate checkpoint is only a diagnostic artifact. Do **not** confuse its hash with the later valid candidate. A failed release attempt in infrastructure run 41412807456 returned GitHub 403; the above learning Release is the actually published checkpoint.

The GitHub release asset digest matches the successful game receipt. **Independent download/load/resume verification has not yet been demonstrated**, and neither `best` nor a supported automatic `latest` pointer is established. Full automated recovery after Artifact expiry is **not yet guaranteed**.

## Workflow and retention

The proposed main `.github/workflows/train.yml` runs weekly (Monday 04:13 UTC) or manually, bounded to 128–20,000 steps and a 180-minute runner timeout. Once reviewed and merged, its successful run also attempts a versioned candidate GitHub Release. The old recent-run restore path still depends on 90-day Actions Artifacts: **Release-based fallback has not been implemented in the latest compatible workflow**. Failed training or model games must not claim successful candidate promotion.

The branch-specific learning workflow already produced the Release above. Do not delete it or all previous models based solely on a more recent model existing.

## Safe manual cloud restore from the confirmed Release

```bash
gh release download v1-learning-9eada5801f99 \
  --repo sstxww/reinforcement-learning \
  --pattern model.zip --pattern model.metadata.json --dir checkpoints
printf '%s  %s\n' dc5195658995358e70c0d565a979b9cf05ccc5e47ae7adaa0a2f078f01cad917 checkpoints/model.zip | sha256sum -c -
python -m tavern_ai.train --steps 128 --seed 42 --resume checkpoints/model.zip --out checkpoints/resumed.zip
```

Run on a compatible GitHub runner using the **learning branch code** that understands schema-2 metadata and the exact pinned TavernGym engine; do not run that model on the older main `train.py` without merging the compatibility changes. This is a **proposed restore procedure**, not a claim that the above sequence passed as an independent run.

`models/registry.json` lists releases and evidence. Candidate means experimental and unpromoted; Latest means **tested for resume**; Best needs a reliable independent paired-seed improvement. No single match or three bottom-place finishes justify promotion.

## Automatic cleanup

`scripts/cleanup_temporary.py --apply` removes only regenerable Python caches and skips Git internals, game receipts, model directories, checkpoints, and research. Dry-run is its default. The proposed main training workflow calls the safe cleanup step after saving the artifact. No irreplaceable checkpoint is deleted by this cleanup.
