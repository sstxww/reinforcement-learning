# s-20261102-fb6a2c91 R001 — V5 integration, Release resume and rank-8 diagnosis

## Session identity and latest-base caveat
- Single independent agent/session `s-20261102-fb6a2c91`, branch `agent/s-20261102-fb6a2c91/optimization-001` (only this session writes it).
- Base main SHA `ef77ae6bc5d9bef09e903fac7705917ec3b7366d` at creation. Current main may change again. PR https://github.com/sstxww/reinforcement-learning/pull/133, intentionally Draft pending CI and verified training.
- V5 instruction read as complete email TXT. Upstream read-only, no official Arena matches, no user local environment. Do not equate a queued/running workflow to a successful training/Release.

## P0 existing PR integration audit — direct GitHub comments published
- PR #93: built `checkpoint_catalog.py` but tests assert canonical model registry has exactly four candidates, and enforce pinned metadata map covers all; current main already has an experimental fifth candidate (V5 1408). The final-head PR CI does not test the merged main. Hold merge until tests are forward-compatible and evaluated against exact latest main. Also existing `release_asset_verifier.py` already provides two-asset hash functionality, so de-duplicate rather than proliferate verifiers.
- PR #15: reported true V2 1280-step model games but no strength increase; Ready status notwithstanding, it depends on Draft #9. #9 exact head has no positive check-run. Do not merge #15 independently or promote V2.
- Other 74 open PRs at initial scan were Draft, many stacked, redundant, or negative. Thus no safe indiscriminate merge performed; no main branch writes.
- Comments sent to GitHub PR #93 and #15, as well as issue #78 with pinned action-decoding evidence.

## P1 isolated reproducibility/custody implementation
- New file `tavern_ai/resume_smoke_fb6a2c91.py` reuses existing canonical `models/registry.json`, `models/release_asset_digests.json` and `tavern_ai.release_asset_verifier.verify_local`, downloads source externally via branch job, fails closed on both mismatched Release hashes, model load, metadata/engine mismatch, missing/changed source, and accidental fresh start.
- Strict `lineage_record`: step counts must advance by actual budget, SHA must change, metadata and optimizer must be retained. Budget limited to exactly 128 incremental steps with unique filenames and branch.
- Tests `tests/test_resume_smoke_fb6a2c91.py` check correct schema, model custody, mismatch, step fraud, unsafe parent overwrite, oversized budget, no claimed model gain. The independent workflow reports targeted regressions passed.
- Source parent: unpromoted `v5-s-20261102-68099929-1408-41428692617`, 1408 genuine cumulative PPO steps, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Pinned engine version 1.1.0, source hash `6d8712c93022ba11`, observe2 dimensions 4017/447/245. Original upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0` from `tavern_ai.contract`.
- Dedicated workflow `.github/workflows/resume-smoke-fb6a2c91.yml` is branch-push-only, unique concurrency, finite CPU budget, original own true-match receipt, model-only canary, conditional n=2 paired heldout eval and **unpromoted** Release after successful resumed checkpoint. No shared main `train.yml` modifications.
- Real workflow https://github.com/sstxww/reinforcement-learning/actions/runs/41450269678: installation, unit-test preflight, pinned engine compilation and original baseline full game **passed**; downloaded parent Release source assets; 128-step actual continuation was still running at writing. Do not claim child model SHA, succeeded 128 updates, durable child Release or model-only rank until run log confirms.

## Own genuine full eight-seat match and receipts
- Own policy: deterministic `baseline`, **not candidate neural model**. Seed 92360, completed=true, 14 turns, 55 decisions, seat0 rank 8; placements `[8,2,4,7,1,3,5,6]`; zero combat truncations or turn-limit end.
- JSON generated in genuine pinned GitHub Actions environment, verified with `python -m tavern_ai.validate_receipt` and committed by branch-only workflow: `experiments/s-20261102-fb6a2c91/001-92360.json`. No synthetic receipt; main CI needs to inspect exact current branch after this evidence.
- Heldout candidate metrics for *this* 128-step smoke: **not yet available**. Historic parent V5 on seeds 99125–99127 ranked [8,8,8] versus baseline [6,8,8] and remains unpromoted.

## P2 actual diagnosis and negative control
- Main committed report `reports/s-20261102-83d91476/001-buy-opportunity-report.json` backed by true Actions #41428098018: candidate V2 seats ranks [8,8] on seeds 45111/45112, zero BUY from **74 buy-legal decision exposures**; IDs 1 and 2 in **222/248** decisions. Baseline same seeds ranks [6,7], 33 BUY / 48 decision exposures. No guard end in model games.
- Read **pinned Rust** `crates/taverngym/src/actions.rs` and `recruit.rs` (upstream read-only): ID1 Refresh, ID2 Freeze, ID7 Cancel, IDs 8–15 Buy; legitimate BUY mask checks paid/free price, hand capacity, gold or health, and Freeze toggles all frozen shop slots. Repeated legal opportunities are correlated and not all economically valuable.
- Draft stacked PR #107 (genuine 9 games) shows an explicit first-legal BUY intervention produced 46 real buys over three games but rank [8,8,8], plus extensive Play/Cancel cycles. So `no BUY` is a confirmed action symptom, **not** a complete causal explanation for rank eighth.
- Upstream `python/taverngym/env.py` describes zero reward until episode completion then placement-scaled reward. Sparse credit assignment is a plausible mechanism, not proven. Need state-transition traces (gold/shop/board/hand), in-turn freeze toggles, pending choose/cancel loops, guarded vs unassisted provenance, and heldout paired seeds before any learning algorithm change or expansion.

## Exact reproduction
- On Python3.12 with pinned engine installed, use branch-specific action workflow. Equivalent verified source CLI:
```bash
gh release download v5-s-20261102-68099929-1408-41428692617 --repo sstxww/reinforcement-learning --pattern model.zip --pattern model.metadata.json --dir checkpoints/source
python -m tavern_ai.resume_smoke_fb6a2c91 --source checkpoints/source/model.zip --out checkpoints/resumed/model.zip --lineage outputs/001-lineage.json --steps 128 --seed 92361
```
- Source bytes **must** pass both-asset hashes and CPU load before model deserialization/gradient updates. Model-pair evaluation uses a separate seed family 92370–92371 if a raw model game completes. No rank claim from assisted/guarded policy or any incomplete game.

## Exit gates/knowledge transfer
No weights are committed to Git. Unique versioned Release is required for child persistence. The job's output/Release results and exact latest-head CI must be verified and documented before considering merge. Branch is Draft; neither latest nor best/champion should change from this research-only smoke.
