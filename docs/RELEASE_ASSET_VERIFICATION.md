# Release asset digest supplement to canonical model registry

**Canonical model registry:** `models/registry.json`, integrated in [PR #87](https://github.com/sstxww/reinforcement-learning/pull/87). This file is NOT another registry and does not define Champion, Latest or role: `models/release_asset_digests.json` only adds expected SHA256 digests for both model.zip and model.metadata.json across six existing public Releases. The values came from the GitHub Release REST API, not from independently downloading all 17-MB checkpoints.

    python -m tavern_ai.release_asset_verifier
    python -m tavern_ai.release_asset_verifier --model-id v2-learning-41413557445 --weights /tmp/model.zip --metadata /tmp/model.metadata.json
    python -m tavern_ai.release_asset_verifier --model-id v2-learning-41413557445 --weights /tmp/model.zip --metadata /tmp/model.metadata.json --check-load

The first command only validates manifests and reconciles the four existing canonical candidates. The second hashes both actual downloaded files, reads pinned engine metadata and training step counter. With --check-load, the third additionally verifies pinned engine installation and MaskablePPO.load. None of these proves true optimizer restoration or full eight-seat model competition. Such tests must be run independently before claiming resumability or Champion promotion. Do not execute --check-load on untrusted files.

No new model weights are committed. No main train/evaluate/canary/workflow code is changed. Companion source of evidence is the own-session baseline canary in `experiments/s-20261102-4ba6d58f/`; NOT a PPO performance test.
