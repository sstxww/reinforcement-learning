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

The original 256-step GitHub Release model was **independently downloaded, SHA-256 verified, loaded, and continued for 128 real PPO steps** by [Actions run 41413508653](https://github.com/sstxww/reinforcement-learning/actions/runs/41413508653). That resumed model reached 384 steps and completed a full eight-seat game (seed 23001, rank 8, 263 decisions) and three held-out matches (all rank 8). The verification and receipt-writing steps passed; the workflow's initial attempt to upload the new 384-step weight to a Release **failed with HTTP 404**, but a subsequent GitHub [Release v1-learning-resume-41413508653](https://github.com/sstxww/reinforcement-learning/releases/tag/v1-learning-resume-41413508653) successfully persisted the exact recovered model SHA256 `79f90ee56e1bf49eac86e39cb76e0df70e2316a5baf5067515bced15649829e7` alongside its match receipt and evaluation. Both the original 256-step Release and the new 384-step Release remain preserved; neither has proven performance gains. Automatic main-workflow restoration after Artifact expiry is still **not configured and verified**.

## Workflow and retention

The proposed main `.github/workflows/train.yml` runs weekly (Monday 04:13 UTC) or manually, bounded to 128–20,000 steps and a 180-minute runner timeout. Once reviewed and merged, its successful run also attempts a versioned candidate GitHub Release. The old recent-run restore path still depends on 90-day Actions Artifacts: **Release-based fallback has not been implemented in the latest compatible workflow**. Failed training or model games must not claim successful candidate promotion.

A separate successful [Learning V2 run 41413557445](https://github.com/sstxww/reinforcement-learning/actions/runs/41413557445) resumed 256 steps for **1,024 additional steps** (1,280 total), played a model-controlled complete game (seed 23002, rank 8), independently evaluated seeds 24000–24003 (placements [8,8,8,8]), and published durable [Release v2-learning-41413557445](https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445), SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. This is currently the **latest saved experimental candidate**, not Best. Its exact Release-based restart has not separately been verified. Baseline on the same four seeds ranked [7,6,8,8], so no model improvement is supported. Preserve both releases with their hashes until a verified promotion and retention decision.

## Safe manual cloud restore from the confirmed Release

```bash
gh release download v1-learning-9eada5801f99 \
  --repo sstxww/reinforcement-learning \
  --pattern model.zip --pattern model.metadata.json --dir checkpoints
printf '%s  %s\n' dc5195658995358e70c0d565a979b9cf05ccc5e47ae7adaa0a2f078f01cad917 checkpoints/model.zip | sha256sum -c -
python -m tavern_ai.train --steps 128 --seed 42 --resume checkpoints/model.zip --out checkpoints/resumed.zip
```

Run on a compatible GitHub runner using the **learning branch code** that understands schema-2 metadata and the exact pinned TavernGym engine; do not silently use the older main `train.py` without compatibility changes. The same download, checksum and 128-step resume sequence **did execute successfully** in Actions run 41413508653; its later extra Release upload failed, as documented above.

`models/registry.json` lists releases and evidence. Candidate means experimental and unpromoted; Latest is the **newest durable checkpoint**, not proof that its own Release-based resume was tested; Best needs a reliable independent paired-seed improvement. No single match or three bottom-place finishes justify promotion.

## Automatic cleanup

`scripts/cleanup_temporary.py --apply` removes only regenerable Python caches and skips Git internals, game receipts, model directories, checkpoints, and research. Dry-run is its default. The proposed main training workflow calls the safe cleanup step after saving the artifact. No irreplaceable checkpoint is deleted by this cleanup.
