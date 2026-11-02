# Round 001 — guarded checkpoint integration and ranked eighth diagnosis

## P0: Current repository
Inspected README, AGENTS, project/session/closed-loop docs, models/registry.json, trainer/evaluator and public Releases/Actions. At audit snapshot main was `db5e23ae8c218808821327d806b05d2604cfadfb` (CI success [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040)). API returned 75 open PRs: 74 Draft and 1 ready. #15 is stacked on unfinished #9, and its own description explicitly says V2 has no paired rank gain. Do not merge. #93/#94 and other model registry proposals overlap already-integrated `models/registry.json`, `tavern_ai/release_asset_verifier.py` and `tavern_ai/model_registry.py`; do not integrate duplicate registry semantics or disregard active authors' Draft gates. CI success on a prior head does not authorize merge.

## P1: Concrete implementation
- `tavern_ai/checkpoint_writer.py`: staged temp checkpoint and metadata writes; file SHA256 attached to saved metadata; hash mismatch or malformed digest blocks subsequent resume.
- `tavern_ai/train.py`: checksum verification before `MaskablePPO.load` (when metadata contains a digest), model-vs-metadata cumulative step count check, parent weight hash provenance, environment close even when load errors.
- `tests/test_checkpoint_writer_s_20261102_001b7da1.py`: 5 offline unit tests; local `pytest` 5/5 passed, syntax compilation passed.
- `.github/workflows/v5-fullmatch-s-20261102-001b7da1.yml`: pinned-engine baseline game seed 91801, artifact receipt; no automatic commit or model promotion.

The ZIP and metadata are two separate renames, not a fully atomic transaction. If interrupted between renames, a checksum-bearing prior metadata should fail on next resume. Historical legacy metadata does not have this protection; require trusted independent release-digest verification. Do not treat this as durable Release publication.

## P2: Confirmed behavior, not guesses
- [Main report 83d91476](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-83d91476/001-buy-opportunity-report.json): 2 genuine V2 games seeds 45111 and 45112, ranks [8,8]. 74 decision points with a mask-legal Buy, zero Buys; 222/248 raw action IDs 1 or 2. Baseline bought 33 times in 48 such exposures, ranks [6,7].
- [Main report ba09e2d4](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-ba09e2d4/002-action-opportunities.json): bounded raw V2 probe on seed 87102 did NOT finish. Among 6000 decisions, 2978 hero powers and 2977 cancels; the last observed turn was 3, indicating a cycling failure. Not a full-match receipt or rank result.
- [Main guarded paired evidence](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json): guard-assisted V2 ranks [8,8] against baseline [5,7]; model bought zero times in both, and one completed game needed 4 guard interventions. Not a pure-model strength claim.
- [Latest candidate registry](https://github.com/sstxww/reinforcement-learning/blob/main/models/registry.json): 1408-step Latest ranks [8,8,8] on three heldout seeds versus baseline [6,8,8]. Champion remains null.
- Separate Draft [#107](https://github.com/sstxww/reinforcement-learning/pull/107) documents 46 forced Buy actions across three heldout games yet [8,8,8] placements, an exploratory negative ablation. It is not a verified causal fix.

Supported diagnosis: legal-buy avoidance and action-loop pathology have direct behavioral evidence; simply adding PPO steps or forced buys cannot yet be justified as a cure. Unproven: whether reward, observation, masking, action semantics or phase economy is primary. Next instrumentation should log state transition after each hero-power/cancel loop, action-family probabilities, gold and board deltas; use a bounded one-variable experiment, with pure and guarded outcomes separated.

## Real work counters
- PR merges: 0 (none satisfied safe gate in owned scope).
- New training steps: 0; new model artifacts: 0; model promotions: 0.
- Local regression tests: 5 passed.
- New game receipts: pending branch-scoped Actions workflow at initial report; do not synthesize.
- Further expansion blocked until session CI, actual own receipt, and strict restore/full-game safety are proven.

## Own independent pinned-engine evidence obtained
[Actions #41449696658](https://github.com/sstxww/reinforcement-learning/actions/runs/41449696658) completed successfully. Downloaded its immutable artifact #13142974966 and transcribed the actual, validated `001-91801.json` into our own `experiments/s-20261102-001b7da1/` directory. Baseline controlled seat 0, seed 91801: complete 8-seat match; rank 7, 18 turns, 46 decisions, 0 combat truncations, no turn-limit ending. Source workflow head `89598b743dc04a5387f70a795e2b8b5fe3943755`. Strict distinction: this is an *infrastructure* baseline receipt; no PPO model was trained, resumed, tested or claimed improved here. Targeted local tests 7 passed. The current PR head's full-match CI is not inferred from this earlier workflow.
