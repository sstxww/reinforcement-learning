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


## R001 verified GitHub Actions outcome (2026-11-02 UTC)
- Full [Actions run 41428217708](https://github.com/sstxww/reinforcement-learning/actions/runs/41428217708): **success** across install, isolated gate tests, complete live PR enumeration, pinned TavernGym build, authentic eight-player game, signed-off receipt validation, and Artifact upload.
- Source-verified receipt `experiments/s-20261102-bb9904e5/001-92031.json`: baseline seed 92031, full-match `completed=true`, seat0 placement **7**, 14 turns, 56 decisions, placements `[7,5,4,6,3,2,1,8]`, no combat truncation or turn-limit end. Run job 125219932593 printed and validated the identical JSON; model SHA null because baseline policy, **not a model victory**.
- GitHub live audit scanned 76/76 open PRs; produced cautious 53 fix/verify and 23 negative/no-gain triage labels (no autonomous merge approval). Main moved during enumeration: `31dc7c82ad2fcba461706b4f324d743b5c1c2b9e` -> `c85d566cccccf5e2ef7de09b6cc95e1aa506da9c`, so no stale merge assumption.
- Committed compact audit summary `reports/s-20261102-bb9904e5/001-audit-summary.json`; complete per-PR JSON available in [temporary 30-day Actions Artifact](https://github.com/sstxww/reinforcement-learning/actions/runs/41428217708/artifacts/13133311312).
- Completed direct PR #75 review as [top-level GitHub comment 6574751195](https://github.com/sstxww/reinforcement-learning/pull/75#issuecomment-6574751195); retained Draft as required by author and because permissions/workflow hardening remain.
- Appended a source-linked, non-causal model behavior diagnosis in `research/sessions/s-20261102-bb9904e5/eighth-place-evidence.md`: true PR #60 low-LR 256-step candidate had zero BUY and 21/36 own END_TURN across three finished games; reference had 20 BUY, 21 forced END and substantial repeated other actions. No proof that learning rate caused the failure; legal opportunity/observations must be measured next.
- **No model trained, loaded, resumed, saved, promoted, or evaluated as a new model in this session**; no claim of stronger model.
