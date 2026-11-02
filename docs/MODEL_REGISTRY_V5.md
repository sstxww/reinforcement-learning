# V5 checkpoint and registry handoff (s-20261102-ba09e2d4)

This is an **audit scaffold**, not a model trainer or a model promotion.

## Truthful model state

- Six GitHub Releases with model artifacts were listed in the initial 2026-11-02 repository inspection; this does **not** verify download, hash, restore, or live games.
- `models/registry-v5.json` catalogs the two historically described candidate releases. Recorded SHA256 strings come from PR #9 and PR #15, **not** an independent rehash of the Release downloads.
- `champion` and `latest_verified_resumable` are `null` until all gates are evidenced. Do not silently promote a failed rank-8 PPO model.
- `tavern_ai.checkpoint_audit_ba09e2d4` verifies offline byte hash, engine metadata, ZIP/optimizer file structure. It **does not load PyTorch weights**.

Example (after obtaining the Release assets from an approved trusted source):

```bash
python -m tavern_ai.checkpoint_audit_ba09e2d4 \
  --checkpoint checkpoints/model.zip \
  --metadata checkpoints/model.metadata.json \
  --expected-sha256 <64-lowercase-hex-from-pinned-manifest> \
  --out reports/<session>/checkpoint-audit.json
```

A reliable restoration gate must additionally execute `MaskablePPO.load`, model inference with legal masks, a bounded 128-step continuation that retains optimizer state and a complete **model-controlled** eight-seat TavernGym game. Only then can the model be marked `resume_verified=true`. For promotion use paired held-out games and uncertainty, not a single match or CI green indicator.

## Priority P0 and P2 observations

- #9 remains Draft; #15 targets branch `agent/learning/v1` and depends on #9. Neither should be merged out of dependency order.
- #25 has valuable strict receipt-integrity tests but remains Draft; integrate via explicit review, not by bypassing draft status. 
- #43 merged during this inspection by another session; do not duplicate an overlapping seat-evaluation PR.
- #60 reports a low-LR PPO policy with zero buy actions in three held-out complete games and 21 model-selected END_TURN actions, while a reference bought 20 times; **without legal purchase opportunity counts, this is evidence of behavioral divergence, not proof of the root cause**.
- Main's shared training workflow restores from a 90-day Artifact and does not itself provide immutable archive-wide model registry guarantees.
- Do not scale PPO until checkpoint restore and action-opportunity diagnostics can be validated.

## Independent evidence

This branch includes a finite, branch-only GitHub Actions workflow to run a real eight-seat baseline canary. It writes its own `experiments/s-20261102-ba09e2d4/001-87101.json` receipt only after real execution. No receipt or PPO training is fabricated. CI must finish and the saved receipt must be inspected before integration.
