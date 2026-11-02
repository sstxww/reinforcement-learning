# Round 001: sparse-zero-counter JSON schema test failure

- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41510359283
- Job: https://github.com/sstxww/reinforcement-learning/actions/runs/41510359283/job/125500328023
- Original head: 6a0eca331c275b0ee2e6a4f5340341e8e4a28f43
- Signature: `FAILED tests/test_v61_raw_economy_9dc0a960.py::test_count_only_actual_raw_buy_and_no_leak_across_turns` with `KeyError: 'unchanged_public_obs_between_decisions'`.
- Cause verified from job logs: Python `Counter` omits zero-valued keys when converted to `dict`, while test and downstream diagnostics expect a stable explicit-zero schema.
- Scope: **accounting serialization**, not TavernGym, policy decoding, weights or inferred placements. Baseline/model steps were not executed in the failed run.
- Minimal change: serialize the eight documented fixed counters explicitly with zero default. Keep regression checking cross-turn equal digest produces zero unchanged-state observations.
- Retry plan: one meaningful code change, one subsequent exact-head isolated CI; restrict workflow push trigger to own probe/test/workflow to prevent bookkeeping commits retriggering expensive dependencies.
- Model train steps this round: 0. Actual completed raw PPO games before retry: 0. No model Release/Champion changed.
