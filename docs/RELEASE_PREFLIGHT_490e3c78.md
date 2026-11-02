# V5 checkpoint archive preflight (additive to merged PR #87)

This feature validates **downloaded** GitHub Release bytes rather than trusting a registry entry. The main branch's `tavern_ai.registry_integrity` from merged PR #87 already checks the registry and SHA256. This narrow R002 extension adds ZIP CRC, archive size boundaries, SB3 policy/optimizer-entry presence, pinned engine metadata, training-step count, and metadata SHA256 agreement. It does **not** instantiate PPO, import untrusted PyTorch pickle, demonstrate optimizer restoration, run PPO gradients, or confer Champion status.

With publicly downloaded `model.zip` and `model.metadata.json` from the same immutable release:

```bash
python -m tavern_ai.release_preflight_490e3c78 \
  --registry models/registry.json \
  --model-id v2-learning-41413557445 \
  --model checkpoints/v5-preflight/model.zip \
  --metadata checkpoints/v5-preflight/model.metadata.json
```

The dedicated read-only Actions workflow downloads both actual Release assets and performs the check, then runs a separately labelled real eight-seat **baseline** match. It stores only compact evidence in a short-lived Actions artifact, never uploads model weights to source control.

The previous wider [PR #89](https://github.com/sstxww/reinforcement-learning/pull/89) was superseded because [PR #87](https://github.com/sstxww/reinforcement-learning/pull/87) integrated the model registry first. There is no justification to merge two same-path registry implementations. Source model V2 heldout placements were 8/8/8/8 and the Champion pointer remains null.
