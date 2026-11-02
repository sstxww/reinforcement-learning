# Model registry integration preflight (V5)

This directory indexes historical **unpromoted** model releases. Its source is the focused, conflict-free model lineage extracted from [infrastructure PR #8](https://github.com/sstxww/reinforcement-learning/pull/8), not a claim that all of PR #8 is ready to merge.

- `models/registry.json`: historical candidates and their declared immutable SHA256 digests, training steps, parent releases, real-match evidence, and limitations.
- `python -m tavern_ai.model_registry`: schema and catalog compatibility verification without downloading weights.
- `python -m tavern_ai.model_registry --model-id ID --model checkpoints/model.zip --metadata checkpoints/model.metadata.json`: after **separately** fetching actual Release assets, verify the file digest, valid ZIP archive, recorded steps and pinned TavernGym version.

The preflight does **not** instantiate PPO, deserialize the optimizer, prove legal masked inference, play a full eight-seat game, or demonstrate a successful resumed training update. These are **separate mandatory checks** before using a checkpoint for continuation. No Champion has been established. The latest 1,280-step candidate has heldout ranks 8/8/8/8; keep it unpromoted. GitHub Actions Artifacts are time-limited, while the six observed GitHub Releases have durable asset entries (remote download and byte verification must still be repeated).

A record sourced from a draft PR is historical *reported evidence* until independently validated by the integrator. Never silently switch training to a model because its index entry says `latest`. Pinned expected engine: 1.1.0, source hash `6d8712c93022ba11`, 4017 float, 447 card, 245 actions.
