# Checkpoint registry (P1)

The registry indexes six existing versioned GitHub Release assets without storing binary weights in Git. The SHA256 values come from GitHub's Release asset index. These are expected digests, NOT independently verified downloaded bytes.

Champion and latest_resumable_id are null because no model has passed all formal admission gates. A published Release, a checksum match, a successful MaskablePPO.load, a true optimizer-state continuation, and genuine completed games are different claims.

Usage:

    python -m tavern_ai.checkpoint_registry --registry models/registry.json
    python -m tavern_ai.checkpoint_registry --registry models/registry.json --model-id v2-learning-41413557445 --weights /private/model.zip --metadata /private/model.metadata.json
    python -m tavern_ai.checkpoint_registry --registry models/registry.json --model-id v2-learning-41413557445 --weights /private/model.zip --metadata /private/model.metadata.json --check-load

The command never downloads files, alters registry flags or trains by itself. Only use trusted downloaded checkpoints, matching exact SHA256 values. For --check-load install pinned TavernGym + sb3-contrib first. SB3 load still does NOT prove a working resume or complete game.

Before promotion: verify actual archive+metadata bytes, pin environment and architecture, perform real PPO optimizer continuation with correct cumulative steps, and collect independently seeded full-game receipts and fallback metrics. Never promote a no-gain pilot based on small samples.
