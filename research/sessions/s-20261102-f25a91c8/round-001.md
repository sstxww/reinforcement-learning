# s-20261102-f25a91c8 · Round 001 — V5 integration, recovery and rank-8 evidence gate

## Provenance and scope
- Read complete 2026-11-02 V5 Gmail TXT (27,248 bytes). No sub-agent/local A11, upstream or ranked Arena operations.
- Branch: `agent/s-20261102-f25a91c8/optimization-001`; base main commit `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`.
- Current snapshot changed during the audit: 75 open PRs initially, then 74 returned by the GitHub Pulls API (73 Draft, one non-Draft).
- Main full-match CI success at run [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040) on `db5e23ae8c218808821327d806b05d2604cfadfb`. A newer main was observed during branch creation.
- No PR merged in this session. The only non-Draft PR #15 targets `agent/learning/v1`, which is Draft PR #9; do not independently merge #15. Draft PR #8 is merge-conflicted; related #82/#83/#84/#86/#92/#93 have overlapping registry/preflight/recovery work, not proven ready by title alone. No reliable integration lock was acquired.

## P0 triage
- **A — verified merge-ready**: none established under strict gates and changing main.
- **B — repair/dependency**: #8 conflicts, #9 remains Draft, #15 depends on #9, #91/#92/#94 show conflicts. Check current head CI before any merge.
- **C — more genuine evaluation**: #68/#75 engine catalogs, #82/#83/#84/#86/#93 recovery/registry modules; separate already merged code from proposed additions and verify exact SHA/optimizer and model load.
- **D — negative/weak findings**: #12, #16, #17, #19, #21 and #107; preserve learning, never promote on weak rank evidence.
- **E — deduplication**: #68/#75 card catalogs and #82/#84/#86/#93/#94/#95 checkpoint audits. Do not merge parallel independent registry schemas blindly.

## P1 current known persisted state
- Main `models/registry.json` has `best: null`, `champion: null`; latest indexed unpromoted experimental model: `v5-s-20261102-68099929-1408-41428692617`.
- SHA256 recorded in registry: `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. This is registry provenance, not a new local byte audit.
- Release shows real model.zip plus metadata. Existing registry records 1,408 steps and [8,8,8] on independent held-out seeds vs baseline [6,8,8]; no improvement verified.
- Main already contains `registry_integrity.py`, `checkpoint_preflight.py`, `release_asset_verifier.py`, and `model_registry.py`; first integrate and test them instead of creating another incompatible checkpoint format.
- No model weights trained, modified, redownloaded, or promoted by this session.

## P2 evidence, not a causal verdict
- Existing real TavernGym report [s-20261102-83d91476](https://github.com/sstxww/reinforcement-learning/actions/runs/41428098018) records **two V2 games**, candidate [8,8] vs baseline [6,7], **74** candidate decision-exposures where a BUY action was legal, **zero chosen BUY**, and **222/248** proposed action IDs 1 or 2. No forced END_TURN in those two games. Decision exposures are correlated, not 74 independent card purchase opportunities.
- Existing real report `reports/s-20261102-68099929/003-buy-opportunity.json` on the 1,408-step candidate shows one paired seed 99128: model 35 legal-buy decision exposures, 0 buys; baseline 21 exposures, 14 buys; both rank 8. Not proof of causality.
- `experiments/s-20261102-83d91476/001-candidate-45111.json` calls the policy `model_guarded`, while recording `guarded: false` and zero forced ends. **Conservative evaluator must not silently relabel this as a raw model**, even when the safety override did not fire.
- Confirmed: substantial *failure to select BUY when legal* co-occurs with rank-8 on these evaluated checkpoints; repeated 1/2 action concentration. Unproven: precise effect of 1/2, economic opportunity cost, reward/encoder/optimizer as underlying cause, or generalizability beyond tested seeds.
- Required next causal test: measure per-action state/gold/board transitions and legal mask, then run one-variable controlled correction with matched held-out seeds and no assisted results mixed into raw evidence.

## P1/P2 concrete change this round
- Added `tavern_ai/paired_evidence_gate_f25a91c8.py` to validate two-sided real-game receipts before rank comparison. Paired by seed AND controlled seat; rejects guard/fallback, truncated, incomplete, bad provenance, mixed model hashes, nonmatching pairs and false model roles; does not promote automatically.
- Added negative mutation tests using **synthetic fixtures, not fabricated games**; CI workflow will independently run one genuine baseline eight-seat game and commit its actual receipt to this session branch if successful.
- Do not claim these existing model reports were generated anew or that this module is a model improvement.

## Status / handoff
- **No new PPO steps (0)**; **no new candidate full games (0)** as of initial report authoring.
- No Champion. No model promotion.
- Do not scale PPO before verifying candidate baseline diagnostics, trustworthy recovery, and causal fix.
- If dedicated CI has not completed, keep new PR Draft and do not claim the canary receipt. Check workflow output for actual run ID and commit SHA before review.

## Verified post-authoring Actions result
- **SUCCESS**: dedicated [run 41450173178](https://github.com/sstxww/reinforcement-learning/actions/runs/41450173178) completed full unit tests, pinned TavernGym compatibility check, and **one genuine eight-seat game**, generated and committed exact receipt `experiments/s-20261102-f25a91c8/001-118573.json`.
- Own independent game result: seed 118573, Baseline seat-0 rank 7, placements [7,6,2,8,3,5,1,4], 50 decisions, 14 turns, no truncation, no turn-limit end. This does **not** test PPO candidate strength.
- Model training performed in this session: 0 steps, no new checkpoint; candidate model games this session: 0. Historical model/guarded results remain attributed to their source sessions.
- Branch PR [#131](https://github.com/sstxww/reinforcement-learning/pull/131) remains Draft pending exact latest-head CI, review, and nonconflicting safe merge ownership.
- Additional verified source-backed P2 docs: `reports/s-20261102-f25a91c8/002-verified-action-semantics.md` (1 Refresh, 2 Freeze) and `003-buy-override-falsification.md` (forced BUY still rank 8, guard reliance worse in PR #107).
