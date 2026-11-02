# Round 001 — independently validate rank-eight BUY telemetry and receipt provenance

## Observed inherited evidence (not produced by this session)

- Current main at session creation `3a745c6f6a48c65528bcbeb81b8627b8db93f046` includes merge of [#176](https://github.com/sstxww/reinforcement-learning/pull/176), plus [main parent CI evidence](https://github.com/sstxww/reinforcement-learning/actions/runs/41510729988) on PR head; do not treat head CI as main postmerge gate.
- Original matched seed **97303** TavernGym games are recorded in `experiments/s-20261103-4fd17801/`: baseline rank 5, BUY 18/25 mask-legal decision exposures; original 1408-step model rank 8, BUY 0/23 mask-legal exposures. The model-controlled game is raw, no guard-forced ending; the 1536-step candidate rank 8 on *different* seed 97304 and was temporarily archived only. These observations show a specific mismatch, not a causal policy fix.
- Other sessions are concurrently handling canonical trainer, persistent Release publishing, action mapping and shared CI; this session changes only unique gate/test/workflow/report paths.

## Falsifiable question and bounded execution

Can the **original registered 1408-step raw model**, on new independent seed 99711 under exactly the same pinned engine and seat as baseline, (a) complete a genuine eight-player game without fallback; and (b) reconcile reported action-family histogram / legally masked BUY exposures with actual decision count and model SHA? The one-seed result is descriptive only and must not be used for promotion or broad causal conclusions.

Own code `tavern_ai/paired_buy_gate_023cd77e.py` verifies two authentic complete receipts with matching engine, seed, policy and exact registered model digest, rejects assisted/fallback counters, checks placement permutations through canonical validator, and verifies opportunity summary internal arithmetic and action-family histogram. Synthetic mutation tests cover wrong identity, manipulated BUY rates, fake ranks and assisted results.

## Budget / custody / failure semantics

One new seed, one raw model, one baseline, **0 PPO training steps** to avoid duplicating known unproductive continuations across 10–20 active sessions. Read-only workflow; 70-minute timeout; no automatic code push; source model only downloaded/read, no Release publish and no registry changes. Store the complete source-run receipts as short-lived Action Artifact until the exact bytes can be independently inspected and committed. A nonterminating raw model records a separate failure diagnostic and never a fabricated placement. Unpromoted parent checkpoint stays immutable.

## Pending verified results

- Workflow run: pending creation and observation.
- Actual own completed game receipts and raw model result: pending.
- Unit tests and exact-head CI: pending.
- Independent model strength or optimizer improvement: not claimed.
- Main merge: not authorized without exclusive serial integration mechanism, current-main compatibility and required CI/reviews.

Next operator must inspect the Actions job and artifact first, preserve original bytes, then decide if the gate and evidence qualify for non-Draft PR and integrator handoff.
