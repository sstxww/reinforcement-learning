# Failure 001 — historical step-counter fixture missing schema

- **PR:** https://github.com/sstxww/reinforcement-learning/pull/196
- **Initial exact HEAD:** `88dc041b5a7951679d861fef900cb1ec75404e0a`
- **Actual failed Actions:** https://github.com/sstxww/reinforcement-learning/actions/runs/41513176363
- **Job:** `tests-and-full-match`, unit-test stage; engine/full-game steps were skipped.
- **Observed tests:** 396 passed, 1 skipped, 1 failed.
- **Failing test:** `tests/test_train_resume_s_20261102_001b7da1.py::test_refuse_wrong_step_count_after_load`.
- **Original expected:** exception `step counters differ` after mock `PPO.load` returns 999 vs metadata 128.
- **Observed:** `Parent checkpoint schema must be an integer` before deserialization.
- **Root cause:** This synthetic historical fixture omitted the checkpoint schema field, despite intending to verify the *later* step-count guard using an otherwise valid parent.
- **Correct fix:** Add `"schema": 1` to this synthetic fixture, leaving production early reject intact. The separate corrupt-SHA test intentionally remains schema-less, since it rejects at SHA verification even earlier. Do **not** weaken the production parser to accept unknown schemas.
- **Retry:** exactly one source/test change after actual failing logs, pending [latest head CI](https://github.com/sstxww/reinforcement-learning/pull/196/checks). No repeated same-SHA retry.
- **Training & game impact:** no PPO steps, no new candidate or Release; original independent full baseline success [41512413873](https://github.com/sstxww/reinforcement-learning/actions/runs/41512413873) remains valid at its original source SHA.
