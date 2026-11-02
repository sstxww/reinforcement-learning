# Release-backed PPO registry (integrator candidate)

This registry is intentionally conservative. It indexes two **existing** experimental
GitHub Releases and their GitHub-API-reported SHA256 digests, without downloading
or promoting either checkpoint. Their unverified state is **not** a claim the authors
failed to load or play them: prior PRs report real games and continuation. It means
this registry's own independent load, resume, and held-out gates have not run.

No Champion is registered. A release listing plus checksum from the Releases API
proves publication metadata, **not** independent artifact download integrity or
working PyTorch deserialization. All numerical competitive claims require full
independent tests on controlled seeds and seats.

## Preflight an existing archived model

1. Download model.zip and model.metadata.json from the corresponding immutable Release.
2. Run:
   python -m tavern_ai.model_registry --model-id v2-learning-41413557445 --checkpoint /path/model.zip --metadata /path/model.metadata.json
3. This verifies SHA256, stable engine/observation/action metadata, PPO optimizer
   member presence, and ZIP CRC without deserializing executable weights.
4. Only in a trusted pinned TavernGym environment, separately run actual
   MaskablePPO.load, inference, a bounded continued learn, save/reload, a complete
   model-controlled eight-seat game, and paired held-out evaluation. Store links
   and SHA of the new checkpoint in its own immutable Release.

Preflight success must never be described as a verified restore or a Champion
promotion. These checks do not alter the existing shared training workflow.

## Known evidence / remaining work

- V1 PR #9: 256 PPO steps; poor full-match placements; author left Draft.
- V2 PR #15: 1280 cumulative steps; depends on V1 PR #9; candidate ranked
  8th in four held-out matches; author did not claim improvement.
- V2 Release sha256: 73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a
- Actual hash-verified re-download, optimizer **usability** and independently
  reproducible 128-step resume are still outstanding for this integration.

A dedicated future integration can connect this safe preflight to the common
train.yml only after demonstrating compatibility with the already-published V1
metadata; do not silently reinitialize a model when an integrity check fails.
