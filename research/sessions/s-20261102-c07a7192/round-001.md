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

## Verified final Actions result (updated after source workflow finished)

- Own unique workflow [41450150026](https://github.com/sstxww/reinforcement-learning/actions/runs/41450150026) completed **success** on source HEAD `2f83885866139d297f4b8ff36489f563d061c894`.
- Offline focused regressions passed; original PR CI 41450222567 ran **241 passed, 1 skipped** but failed the separate evidence gate because it executed before this own match receipt was committed. This is a sequencing failure, not a test failure. Re-run current PR CI after evidence commits; do not merge until success.
- Actual baseline match seed **76012**: place **8**, 15 turns, 30 decisions, completed and validation succeeded, 0 truncations. Genuine receipt `experiments/s-20261102-c07a7192/001-76012.json` was committed by isolated workflow.
- Downloaded actual versioned parent V5 1408-step Release `v5-s-20261102-68099929-1408-41428692617`; parent SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, actual both asset digest/optimizer ZIP/CPU inference checks succeeded.
- **128 genuine PPO steps completed**, cumulative **1408→1536**, metadata verified in Actions. Resulting resumed model SHA256 `c1851820a7cbd353b8d8c91b4a446c512c4f6ba3f7048259da3f61ad932be0d1`.
- **Model-controlled** authentic eight-seat match seed **76013**: place **8**, 16 turns, 122 decisions, completed, zero combat truncations. Its model receipt was read verbatim from verified workflow logs and committed as `experiments/s-20261102-c07a7192/002-76013-model.json`. Machine-readable replay audit is in `reports/s-20261102-c07a7192/001-release-resume.json`.
- Newly resumed weights are in 30-day GitHub Actions diagnostic Artifact **only**, not an immutable Release; **not durable**, never Champion. Source 1408-step checkpoint remains safely preserved in Release. There is no paired heldout gain or learning signal established from this one new model match. Further PPO expansion is blocked pending behavioral diagnosis and durable new checkpoint publishing.

## Focused cross-session P2 evidence (no invented new games)

- Main canonical source `reports/s-20261102-68099929/003-buy-opportunity.json`: V5 1408-step game seed99128 has 35 mask-legal BUY decisions, 0 buys, rank8; same seed baseline 14 buys out of 21 legal BUY decision states, rank8. Small n=1 pair.
- Main `reports/s-20261102-83d91476/001-buy-opportunity-report.json`: two V2 PPO games rank [8,8], 74 mask-legal BUY decision states, 0 purchases, 222/248 actions raw 1 or 2; baseline ranks [6,7], 33 buys. These are real matched games, not a mechanism causal test.
- Draft dependent PR #107 (not merged) reports 46 forced legal buys in 3 games still ranked [8,8,8], with Play/Cancel loop symptoms; a negative **small-sample ablation**, not evidence that forced buying teaches a good policy.
- Main guard experiment `reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json`: guarded V2 still two rank8 and no buys. Prioritize state progression, action-family logits/entropy, observed gold, Play/Cancel loops and reward consistency over blind training scale-up.
