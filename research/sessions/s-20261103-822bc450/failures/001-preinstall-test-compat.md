# R001: eager checkpoint-collision check changed interrupted-save exception

- FAILURE_RUN: https://github.com/sstxww/reinforcement-learning/actions/runs/41512234993
- EXACT_HEAD_SHA: 6995b8038154b689fb83178f53cbda5ffb37c165
- JOB: 125506722076
- FAILED_TEST: tests/test_checkpoint_writer_s_20261102_001b7da1.py::test_interrupted_save_preserves_existing_pair
- Observed: 12 passed, 1 failed; original test expected StubModel.save to raise RuntimeError("interrupted"), but our initial upfront path-exists check raised FileExistsError before invoking model.save.
- Proven cause: eager collision precheck changed control flow and preempted the original interrupted-model-save regression contract. This did not expose a checkpoint overwrite or corrupt an actual model.
- Fix commit: a4765f2cb76e79af3017977cd150a9bcf957300a removes only eager precheck. The os.link exclusive final install remains; existing final paths still fail closed when writer successfully stages a new candidate.
- The authentic full-game step was SKIPPED after failed tests. No receipt/game result, no optimizer training, no Release should be claimed from this run.
- Retest: run same focused tests on corrected HEAD, then pinned TavernGym genuine eight-seat baseline; do not retry identical failing SHA.
