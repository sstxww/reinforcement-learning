# Round 001 — assistive-action alias bypass

- Role: WORKER; task `evaluation/raw-assistance-alias-bypass`; base main `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`.
- Priority: P0/P3 canonical evaluation integrity, before any large-scale PPO training.
- P0 sync: original main observed `df07dd23c99079449417fa8e645cf2b6c76b9704`, advanced to `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`. #117 merged by OTHER sessions; #165 token-scope, #161 resume provenance, #163 action-state probe are open DRAFT; #15 is Ready but stacked on PR #9, not eligible for direct main merge.
- Registry snapshot: `best = null`, `champion = null`, unpromoted 1408-step Release `v5-s-20261102-68099929-1408-41428692617`, exact weight SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, heldout ranks [8,8,8]. This model is not an established improvement.
- Engine contract: TavernGym 1.1.0, source `6d8712c93022ba11`, observe2 floats 4017, cards 447, actions 245, upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce` and patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Root-cause hypothesis: `paired_receipt_gate_v5._guard_count` omitted two positive assisted-action aliases that the main evaluator otherwise knows (`fallback_actions`, `guard_forced_ends`). As a result, a record from a guarded run could enter the raw PPO comparison as unguarded.
- Minimal fix: classify both aliases at receipt root and in `opportunity_diagnostics.counts`, retain fail-closed non-integer/negative counter handling; avoid another duplicate evaluator.
- Verification: synthetic-only positive and negative tests in dedicated file; real CI and authentic baseline canary pending. The smoke is infrastructure assurance, not model strength.
- Current iteration actual training 0 steps; real new model vs baseline comparisons 0; no model weights, no Release, no promotion.
- Fixed seeds: smoke seed 99631 is *not* heldout PPO strength evidence and not a training seed. Ranking claim: none.
- Safety: read-only Actions token, one bounded CPU smoke, no Arena.
- Integration instructions: only appointed INTEGRATOR should reconcile this small canonical patch against subsequent main and #144/#145/#148, review latest-head full-game CI, and decide merge.

## Verified execution update (2026-11-02 19:29 UTC)

- Exact source-head isolated [Actions #41510061335](https://github.com/sstxww/reinforcement-learning/actions/runs/41510061335) **completed successfully**: focused original + new regression tests, pinned-engine bootstrap, engine contract, independently executed full eight-seat baseline canary and receipt upload. This is not a trained PPO match.
- Genuine receipt `experiments/s-20261103-6b83cecd/001-99631.json` ([source receipt commit](https://github.com/sstxww/reinforcement-learning/commit/ebc77f5589046731846f65ebf5b7a7263c98116c)): seed 99631, baseline seat 0 **rank 3**, complete ranks [3,4,8,6,5,2,1,7], 13 turns, 57 decisions, no simulator guard; source workflow SHA `250869ead9c7850a6d8e117f25dce133aad3ed71`.
- Machine-readable verification: `reports/s-20261103-6b83cecd/001-guard-alias-regression-and-baseline.json`.
- NEW PPO steps **0**, NEW model Release **none**, Champion/Best not changed. This fix closes an evidence-label integrity hole, not a model-strength problem. Large-scale training remains gated by raw rank-eight behavior and INTEGRATOR budget.
- Latest PR head CI must be checked independently after Draft PR creation; never misreport this older workflow-source success as final PR-head CI.
