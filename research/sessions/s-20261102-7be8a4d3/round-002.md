# s-20261102-7be8a4d3 Round 002 — Deduplicated Release verifier and true 1408-step checkpoint

## Why this round exists
During R001, another integrator safely merged the richer historical model registry into main (main `c85d566...` and later). Old [PR #97](https://github.com/sstxww/reinforcement-learning/pull/97) attempted a smaller `models/registry.json`, now conflicts. Rather than overwrite merged research, this new round starts directly on main `744d33c1d975347d3939158cb9369e99fc729796` and **does not modify `models/registry.json`**. It provides new verifier and actual real-game/release evidence only.

## Reproducible verified source and genuine resume
- Source: GitHub Release `v2-learning-41413557445` actual 1280-step model, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- Original [Actions 41428181901](https://github.com/sstxww/reinforcement-learning/actions/runs/41428181901) ran Python unit tests, pinned TavernGym 1.1.0 with source hash `6d8712c93022ba11`, downloaded model/metadata and checked SHA. It loaded the model, ran a full model-controlled eight-seat game, actually called `python -m tavern_ai.train --steps 128 --seed 42 --resume checkpoints/model.zip --out checkpoints/resumed.zip`, then completed a second full model-controlled eight-seat game.
- New checkpoint steps **1408**, SHA256 `250be6159508fdd1ef91abb6c7277efe32fa49c726ea347923f18f6a4765e0f0`. New independent GitHub prerelease `v5-recovery-s-20261102-7be8a4d3-41428181901`, marked experimental, not Champion.
- Real eight-player game receipts: `experiments/s-20261102-7be8a4d3/001-baseline-23002.json` (rank8,40 actions), `001-original-23002.json` (rank8,134 actions), `001-resumed-23002.json` (rank8,134 actions), each `Game.is_over()` true, no truncated combat/turn guard, and model games used genuine model policies without fallback.
- First workflow reported success but `gh release create path#label` named actual assets `resumed.zip`, not `model.zip`, so first readback failed. This is preserved in `research/sessions/s-20261102-7be8a4d3/failures/001-release-asset-name.md`; the report from first run truthfully remains `release_redownload_verified:false`.
- Independent follow-up [Actions 41428877707](https://github.com/sstxww/reinforcement-learning/actions/runs/41428877707) **succeeded**: downloaded original model asset, checked its SHA and step count, uploaded correctly named `model.zip` and `model.metadata.json`, downloaded the renamed assets independently, validated exact SHA and matching metadata. A separate `001-release-reverified.json` records true. This is verified durable stored weight, distinct from expiring 30/90-day artifacts.

## Code and tests
- `scripts/verify_release_candidate.py` accepts the existing richer main registry schema, checks pinned observe2 dimensions, existing candidates, hashes, metadata, training steps, optional full compatibility and refuses Champion promotion.
- `tests/test_release_candidate.py` covers registry parsing, tampering, duplicate IDs, wrong dimensions, mismatched checkpoints and steps; full repo CI still must pass on new integration branch final head.
- `models/candidates/v5-s-20261102-7be8a4d3-1408.json` is isolated evidence manifest only; the global registry `models/registry.json` remains intact for integrator-controlled updates. No large binary committed to git.

## Strength/diagnostic interpretation
One known seed, all three roles placed 8th. This **only verifies checkpoint continuity and playable inference**. It is not independent heldout improvement, no top-four claim, no self-play, no ranked Arena. P2 report shows divergent low-LR model behavior with zero BUY and frequent END_TURN vs another candidate's action loops, but mechanism requires buy legal-mask and gold telemetry before tuning. Next propose paired seat-rotated evaluation and reproducible buy-legal opportunity measurement before scaling further.
