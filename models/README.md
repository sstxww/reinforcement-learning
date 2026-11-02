# Checkpoint registration (V5 review candidate)

This is a content-addressed manifest tool for existing MaskablePPO checkpoints. It never creates or promotes a model, uploads weights, or claims that a Release is downloadable or resumable. No Champion is designated.

Usage:

    python -m tavern_ai.checkpoint_registry record --model checkpoints/model.zip --metadata checkpoints/model.metadata.json --model-id m-example-0001 --source-commit FULL_40_CHAR_SHA --manifest models/manifests/m-example-0001.json
    python -m tavern_ai.checkpoint_registry verify --model checkpoints/model.zip --metadata checkpoints/model.metadata.json --manifest models/manifests/m-example-0001.json

Records contain engine fingerprint, algorithm, cumulative training steps, immutable ID/source commit, parent, both SHA256 hashes, byte count and optionally a storage URL. Existing manifest paths cannot be overwritten. All verification flags default to false, including persistent storage, model load, optimizer resume, genuine match and competitive promotion. File-hash verification is not a load or resume test.

The existing main train.yml restores only expiring Actions Artifacts; this proposal does not change that shared workflow. Follow-on work must independently redownload Release weights, verify SHA256, load and resume the model, run authentic full eight-seat matches, perform seed-and-seat-controlled comparisons, and only then connect an approved registry to training. Large model.zip files must not be committed to Git.
