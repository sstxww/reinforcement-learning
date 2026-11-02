# Round 001 — Promote existing strict receipt verifier into PR evidence gate

## Hypothesis and prior evidence

The shared PR evidence script accepted any eight rank integers in 1..8 because it called the historical `tavern_ai.validate_receipt.validate`, which did not require a permutation or pinned engine provenance. The repository already contains `tavern_ai.receipt_integrity.validate_integrity` with stricter checks and mutation regression tests. No new validation algorithm is needed: connect this existing verified implementation to the integration entrypoint.

## Actual code and test

- Base main: `db5e23ae8c218808821327d806b05d2604cfadfb`.
- Branch: `agent/s-20261102-86664ac4/optimization-001`.
- Changed shared script: `scripts/check_pr_evidence.py`, import/call existing strict checker.
- New tests: `tests/test_pr_evidence_strict_s_86664ac4.py`, explicitly synthetic fixtures, not game results.
- New branch-only finite workflow: `.github/workflows/receipt-strict-s-20261102-86664ac4.yml`; scoped triggers, no shared checkpoint writes.
- GitHub Actions run https://github.com/sstxww/reinforcement-learning/actions/runs/41449621980 **SUCCESS**: test step, pinned TavernGym 1.1.0, game, strict validation, authentic receipt commit, artifact step all success.

## Actual independent complete game

- `experiments/s-20261102-86664ac4/001-96641.json` (generated and committed by successful workflow, not synthesized).
- Seed 96641; player-0 `BaselinePolicy`, seven simulator rule bots; `Game.is_over()==True`, player rank 4; 14 turns, 70 decisions, placements `[4,1,2,7,5,6,8,3]`.
- `truncated_combats=0`, `turn_limit_end=false`, engine hash `6d8712c93022ba11`, observe2 contract 4017 features / 447 cards / 245 actions.
- No PPO train steps, no model checkpoint or resume, no policy-strength claim. This proves infrastructure can run and the gate accepts the real receipt.

## Integration and research carryover

- GitHub #103 and #107 reviewed on latest PR HEADs; both stay Draft because #107 depends on #103 and their diagnostic code overlaps existing main; reported ranks remain eighth despite purchase override.
- Current main after concurrent updates: `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`; the target script still uses legacy validation there at last check, so the P0 correctness gap remains open.
- The latest durable candidate in canonical registry is 1408 PPO steps, experimental/unpromoted. Stored Release does not imply competitive improvement or prove latest-tag optimizer continuation.
- Shared training workflow still has implicit fresh restart on unavailable time-limited artifact; do not expand PPO training until restored Release asset + optimizer state, evaluation and archive contracts are made fail-closed.
- A merge should be considered only after latest-HEAD CI, evidence and compatibility review; verify main CI post-merge. No ranked Arena.
