# Round 001 — prevent falsely pooled 1536-step evidence

Starting main `c1b828734527bae6141805581693d890cc3bff94`; unique task claim `claims/v7/audit-1536-candidate-censoring` created atomically before work, and dedicated branch `agent/s-20261103-4c5fcc9a/optimization-001`.

Evidence inherited from main, not produced by this session: `experiments/s-20261103-4fd17801/001-baseline-97303.json` seed 97303 baseline rank 5; `002-source-model-97303.json` same seed raw registered 1408-step model rank 8, 0 BUY on 23 legal-BUY decision exposures; `003-candidate-97304.json` 1536-step raw model rank 8 at seed 97304, model SHA `e9eb78bb100dd2398258d7f7797b7fc589bc3ef7abd0badca34c964823a04e13`, stored in a temporary 14-day Artifact only. Separately, `reports/s-20261103-c1452513/002-1536-candidate-heldout-failure.json` identifies a DIFFERENT 1536-step SHA `b2b4a1039ca0f5c0e8475646c80996601d26efd081be533972638607c277508d`, whose candidate held-out evaluation did not finish; no final placement is known.

Minimal hypothesis: identical cumulative training steps tempt improper aggregation of different checkpoint weights and censoring of incomplete games as rank 8. New offline auditor binds exact SHA, pinned engine, raw policy, same-seed source-vs-baseline, and rejects assisted or incomplete receipts; negative tests cover mutation cases. Historical evaluation is descriptive (n=1 paired parent-vs-baseline, rank 8 minus 5 = +3 worse) and does NOT establish candidate-vs-parent gain. This script is NOT a replacement for canonical evaluator or a simulator.

Local regression: `python -m pytest -q tests/test_v7_candidate_censor_audit_4c5fcc9a.py` yielded 12 passed on local copy. GitHub Actions own baseline, report artifact, exact HEAD CI, PR review, lease and main merge are pending and must be verified rather than presumed.

No training steps, no new model Release, no raw candidate game in this session. The existing source results are explicitly inherited; do not claim own new model evaluation. Expected end state: independent reproducible report + actual own eight-seat baseline receipt + non-Draft integration candidate.
