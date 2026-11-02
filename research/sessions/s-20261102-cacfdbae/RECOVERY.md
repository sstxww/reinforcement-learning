# V5 R001: exact checkpoint lineage and recovery

**This document describes real stored assets, not a Champion promotion.** Pinned TavernGym 1.1.0 engine fingerprint `6d8712c93022ba11` and observe2 dimensions 4017/447/245.

Source Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445
- `model.zip` SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- `model.metadata.json`: historical schema 2; saved total PPO steps 1280.
- Independent Release download/metadata+optimizer+CPU load and original-model completed game verified in [Actions #41428441545](https://github.com/sstxww/reinforcement-learning/actions/runs/41428441545).

New unpromoted **smoke** Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-cacfdbae-smoke-128
- Asset names are **`resumed.zip`** and **`resumed.metadata.json`** (not `model.zip`).
- `resumed.zip` GitHub asset SHA256 `f0d9c459b9a96e45c206f2a00196d3d7d3c887bb6fb907918c17c8e3010a2b39`; metadata contains 1408 total steps. Training additional **128** steps completed.
- Genuine model game seed23002 rank8; two independent heldout seeds both rank8 against rule baseline ranks7/6. **Not Best.**

To retrieve the candidate for later local inspection, after installing the pinned dependencies and GitHub CLI and authenticating safely:

```bash
mkdir -p checkpoints
gh release download v5-s-20261102-cacfdbae-smoke-128 \
  --repo sstxww/reinforcement-learning \
  --pattern resumed.zip --pattern resumed.metadata.json --dir checkpoints
echo 'f0d9c459b9a96e45c206f2a00196d3d7d3c887bb6fb907918c17c8e3010a2b39  checkpoints/resumed.zip' | sha256sum --check
mv checkpoints/resumed.zip checkpoints/model.zip
mv checkpoints/resumed.metadata.json checkpoints/model.metadata.json
```

These commands have **not** been executed against the newly created smoke Release by this session. A future resumed training job must independently verify byte integrity, matching metadata, model load, and actual continuation; do not silently treat stored GitHub digest as an independent recovery test. The isolated Release inventory resides at `models/release_inventory_v5.json`; this does **not** override the established registry proposed in Draft PR #8.
