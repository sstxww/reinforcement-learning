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
