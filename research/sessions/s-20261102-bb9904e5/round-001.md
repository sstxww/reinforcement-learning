# s-20261102-bb9904e5 Round 001 — P0 conservative integration triage

## Provenance and scope
Read Gmail V5 full TXT (27,248-byte attachment). Branch created from main `31dc7c82ad2fcba461706b4f324d743b5c1c2b9e`; independent files only. Pinned TavernGym contract: 1.1.0, source hash `6d8712c93022ba11`, observation floats 4017, cards 447, legal mask actions 245 (from main contract, requires Actions verification).

## Actual repository evidence at initial audit (volatile snapshot)
- Main `3c65ffd0380d6269e6b39c7bf1ca2d84281546d8` at first inventory, later `31dc7c82ad2fcba461706b4f324d743b5c1c2b9e` at this branch creation; concurrent merges mean any single audit snapshot expires quickly.
- Open PR count initially 63, later 67; all but PR #15 marked Draft at 67-PR snapshot. #15 targets `agent/learning/v1` instead of main (stacked dependency).
- #8 infrastructure: Draft, `mergeable_state=dirty`; includes valuable Release registry and recovery helpers but conflicts with main workflow/training/CI/receipt changes. Do NOT merge wholesale without extracting/validating work. A concurrent integrator already posted extraction work to #8; avoid duplicating it.
- #60 PPO telemetry records 3 independent low-learning-rate games with missing purchase behavior; evidence suggests a basic-action failure but does not alone establish exclusive causal root. Strategy-only negative PRs should not be upgraded.
- Six GitHub Releases provide downloadable model assets; Release existence/digest does not prove this session loaded/retrained weights. Last named V2 candidate 1280 PPO steps, heldout ranks [8,8,8,8], not Champion. Other sessions currently auditing checkpoint restore; do not duplicate their work.
- Latest main full-game CI was in progress at initial audit; prior main SHA had passed. No current-main success claim is made.

## New narrowly scoped P0 deliverable
`scripts/v5_pr_gate_bb9904e5.py` inventories every open PR, fetches live main SHA, each latest PR head and same-head PR-triggered full-match CI, merges-without-checks NEVER allowed, distinguishes Draft, conflict, stacked dependency and negative experiments. Report includes a second main-head read to signal concurrent modifications. Tool cannot approve/merge automatically and labels any category-A PR manual-review only. Offline non-network tests in `tests/test_v5_pr_gate_bb9904e5.py`.

## Stage gates and limits
No training or model promotion; complete baseline canary and CI to be verified from this branch before PR review. A clean category-A line is only a preliminary engineer-review queue, never sufficient merge approval. Do not silently claim game wins or restoration.

## Work remaining
Review newest actual results and current main; distill safe infrastructure PRs under conflict ownership; unify Release-based resume, evaluation metrics and model registry only after separate integration approval; instrument legal purchase opportunities vs no-buy and verify eighth-place root; then test small PPO intervention before expansion.
