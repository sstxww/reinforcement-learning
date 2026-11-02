# s-20261102-83d91476 — R001 V5 legal purchase-opportunity diagnostic

## P0 and P1 gates checked before writing
- Source Gmail V5 instructions read completely, 2026-11-02.
- Main at branch creation: `31dc7c82ad2fcba461706b4f324d743b5c1c2b9e`. Exact working branch: `agent/s-20261102-83d91476/optimization-001`.
- Snapshot: 64 open PRs (63 Draft); only ready PR #15 depends on Draft #9, and Draft #8 has merge conflicts and owns registry/storage work. No bulk merge justified.
- Main advanced concurrently (#25, #43, #69 already landed); re-check merge base and main CI before any merge.
- P1 checkpoint integrity/storage is actively covered by multiple separate in-flight PRs (#8, #79, etc); no changes to their shared interfaces made here.

## P2 falsifiable diagnosis
- Existing PR #60 reports 0 BUY actions and many policy END_TURNs for low-LR PPO, but has no denominator of *legal BUY opportunities*. That means "never buys" alone cannot identify cause.
- This isolated tool counts pre-action legal BUY exposures (mask indices 8..15), model-chosen END_TURN with a legal BUY, and forced safety ends separately.
- Compares previously released **unpromoted V2 model** with existing baseline on matched, new seeds 45111 and 45112; does **not** train or change policy. Both use the same verified game engine.
- Does not estimate affordability, quality, or precise independent opportunities; multiple exposures in one turn are correlated.
- Hard-coded V2 Release digest comes from earlier verified PR #15; Action will verify actual downloadable bytes before use.
- A success on the baseline full-game CI is not a success for a model game; model-game outcome requires this branch's workflow artifact.
- Promotion is forbidden regardless of two-game outcome.

## Verification and handoff
- Synthetic unit tests cover zero-legal-buy states, policy vs safety END_TURN, illegal decisions, and summary guards.
- Real end-to-end verification pending `.github/workflows/buy-opportunities-s-20261102-83d91476.yml`; no true-game evidence or training steps claimed until this workflow completes.
- On success, read artifact `opportunities.json`, compare `policy_end_with_buy_legal`, `buy_legal_exposures`, `guard_forced_end`, model vs baseline and per-turn breakdown.
- If model is rank 8 despite many legal buys and ends with buy still legal, target early end-turn behavior or action-probability defect, not more PPO steps.
- If buy was rarely legal, inspect engine state/economy and action-mask semantics before proposing any loss change.
- Never enter official ranked arena; never modify upstream.

## Verified Actions results (after original R001 draft)

- Actual branch-specific run: [#41428098018](https://github.com/sstxww/reinforcement-learning/actions/runs/41428098018) **SUCCESS**, pinned engine 1.1.0 / hash `6d8712c93022ba11`; V2 Release SHA256 verification **passed**; artifact [#13132408776](https://github.com/sstxww/reinforcement-learning/actions/runs/41428098018/artifacts/13132408776).
- Original PR CI [#41428144058](https://github.com/sstxww/reinforcement-learning/actions/runs/41428144058): 83 tests passed, 1 skipped; it failed only because independent receipt was not yet committed. This follow-up adds compact authentic model/baseline receipts from the downloaded artifact.
- V2 model finished 2 authentic matches on held-out seeds 45111,45112 with ranks **[8,8]**, no forced ends, **0 BUY** despite **74 legal BUY decision exposures**. The baseline ranked **[6,7]**, with **33 BUY** across 48 legal BUY exposures.
- Model actions overwhelmingly ID 1/2 (**222/248**), no guard. Raw action categories / state-delta semantics still need source and trajectory verification. No model update, no inference rescue, no new PPO training.
- These data **refute** the narrow hypothesis that no purchases occurred *because no buy was legal*. They do **not** establish model probabilities, exact economy loss or a causal fix.
- Permanent compact report: `reports/s-20261102-83d91476/001-buy-opportunity-report.json`; full diagnostic report in finite-retention Action artifact, source SHA recorded. Each compact receipt preserves genuine game fields; it is a derived subset, not a fabricated game.
- Next: audit ID 1/2 engine semantics, instrument state progression and illegal mask/opportunity, then a one-variable correction; do not scale training yet.
