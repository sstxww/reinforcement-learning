# V5 session s-20261102-c07a7192 — round 001

## Verified starting state
- Started 2026-11-02 from main `db5e23ae8c218808821327d806b05d2604cfadfb`. The corresponding main CI 41432038040 completed successfully.
- GitHub REST open PR inventory: **75 open, 74 Draft**; only non-Draft #15 targets `agent/learning/v1`, not `main`. No direct merge was attempted without a fresh exact-head gate and integration ownership.
- Existing main `models/registry.json` has **no Best or Champion**. Its latest experimentally unpromoted candidate is V5 1408-step `v5-s-20261102-68099929-1408-41428692617`, published to an immutable versioned Release. The existing repository reports heldout ranks [8,8,8] vs baseline [6,8,8] on three paired games. This is not competitive improvement.

## Verified P1 defect
At starting main, `.github/workflows/train.yml` only uses the last successful Actions Artifact; when none is downloadable, it deletes the missing source and begins from random initialization. Artifacts expire; this breaks verifiable training lineage. Current `tavern_ai.train` requires matching engine metadata but did not independently validate Release weights before restoration.

## Own bounded change
- Added `tavern_ai/release_restore.py` that selects the canonical registry's latest unpromoted full-game model, uses the already merged `registry_integrity`, `release_asset_verifier` and `checkpoint_preflight`, validates actual downloaded asset bytes, optimizer ZIP and engine metadata, optionally proves CPU inference, then publishes the two files as a directory only after all gates.
- Updated **only on this isolated branch** the shared `train.yml` to resume from this durable Release, and to **fail closed** instead of silently initializing random weights.
- Added offline test cases for malformed latest provenance, missing or tampered Release, preserving prior state and forbidding implicit cold starts.
- Branch-specific real TavernGym canary and 128-step smoke workflow will be checked separately; existing PR CI must pass at **final** head before review. No upstream write, Arena play, policy promotion or cross-agent file modification.

## P2 status / evidence boundaries
Current main already contains several independent real-game rank-8 probes: V2 PPO frequently selects Refresh/Freeze/Cancel and does not choose BUY even when mask-legal. Existing complete matches do not establish that a simple forced BUY override improves rank; some reported interventions still rank 8. Check action legality, economic state, loops and paired outcomes before further PPO expansion.

## Honesty gate
At the time this report was first committed, this session had performed **0 PPO training steps, 0 fresh eight-seat games and 0 new weights**. None of the existing Release or other agents' receipts is represented as this session's own run. The isolated workflow, if successful, must preserve an authentic own eight-seat receipt under `experiments/s-20261102-c07a7192/` and an actual Actions run URL. An uploaded Artifact is temporary, not durable model storage. Leave PR Draft until this is independently confirmed.

## Next check
Confirm branch workflow, own genuine receipt, exact-head PR CI and reviewer approval. If V5 strict model-controlled smoke fails, report real error and do not publish or promote a model. Do not touch the shared main training workflow without safe integration ownership.
