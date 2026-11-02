# V6.1 round 001 — paired raw/guard evidence integrity

## Scope and causal hypothesis
WORKER `s-20261103-17407c36` started at main SHA `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`; atomic task claim `claims/p3-paired-guard-provenance`. Existing `tavern_ai/paired_receipt_gate_v5.py` has a fail-closed check, but as read from main it enumerated only `guard_forced_end`, `forced_end_count`, `fallback_count`, `safety_fallback_count` and nested `counts.guard_forced_end`. Another main probe emits `guard_interventions` and `policy_variant=hero_cancel_guard_v1`; those fields were not used.

**Falsifiable test:** A synthetically valid model receipt marked `guard_interventions=1` could previously be accepted as raw by `compare`. After patch, undeclared interventions should fail; a declared assisted variant should stay diagnostic even if its guard count was zero in this game. These synthetic rows are only validator tests, NOT games.

## Changes
- Extend counter extraction from top-level, nested opportunity diagnostics, and opportunity summary; reject non-integer/negative guard counts.
- Separate assisted policy tags from pure model evidence on declared variants.
- Add synthetic-only regression test covering hidden counters, variant classification and no-intervention control.
- Run one original TavernGym eight-seat baseline canary on bounded, branch-specific Actions job; it proves simulator/CI accessibility, **not PPO competence**.

## Provenance and budgets
Pinned engine TavernGym 1.1.0, source hash `6d8712c93022ba11`, observe2 4017 float / 447 cards / 245 actions. Candidate model training: **0 new PPO steps** (no large training authorized for WORKER without a main gate). Canonical latest experimental source is an existing 1408-step Release; not modified, not promoted. Planned canary seed 99412, controlled seat 0, scripted opponents, baseline, no guard. Original model candidate evaluation: **none** in this round. Any future failed run or incomplete game is an error log, not a rank-8 placement.

## Gate and handoff
This PR must remain Draft until its exact head has green CI and own original full-game receipt archived. Main merge reserved to INTEGRATOR. No reset of model registry, no official Best, no weighted performance claim. Next hypothesis after evidence: use observed explicit guard fields to distinguish genuine raw PPO failure from assisted completion.
