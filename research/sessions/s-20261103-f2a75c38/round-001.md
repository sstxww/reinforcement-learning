# R001 — loaded SB3 step-lineage gate, original eight-seat baseline evidence

**R001 / s-20261103-f2a75c38; TASK_KEY `audit/legacy-release-loaded-timesteps`; base main `990acd21d598a34a554a80c50089a8f1a9423ac4`.** Work is additive and does not modify shared train.py/train.yml/evaluate.py or registry.

## Inherited result and falsifiable defect

Main `tavern_ai/model_registry.verify_local` checks the model ZIP SHA, the presence of optimizer, ZIP CRC, engine metadata and optional CPU-load observation/action layout. With `load=True`, it does **not** compare `MaskablePPO.load(...).num_timesteps` to `model.metadata.json.total_timesteps`, making an incorrect cumulative training lineage possible despite matching archive and metadata hash. New read-only `tavern_ai.release_step_audit_s_f2a75c38` CLI composes existing checks and verifies this extra equality. Boolean, absent, zero, stale or mismatched numbers fail closed. No optimizer training is claimed by checking a counter.

## Actual execution and original receipt

- Initial commit `236c6f2aebd45920dce2857e8d1d13a916bf4f1f`; own branch-scoped workflow [#41512333870](https://github.com/sstxww/reinforcement-learning/actions/runs/41512333870), run completed success. Regression tests use **synthetic** ZIP and fake SB3 model. The pinned TavernGym 1.1.0 bootstrap and contract steps passed.
- Genuine full TavernGym game was run by **baseline**, not a PPO checkpoint. Seed 998237, seat 0, ranking [8,1,5,3,6,4,2,7], seat0 rank 8, 18 turns, 40 decisions, game completed, truncated combats 0, turn_limit_end=false. Read original JSON from Actions Artifact #13173537220 and recomputed SHA256 `03de4f520391607a38745773e2206664661fe3751718680608f726e206983cae`. Copy in `experiments/s-20261103-f2a75c38/001-998237.json` is original evidence, **not** a synthetic model fixture.
- New trained steps: **0**, model-only games **0**, held-out paired comparisons **0**, no model-parameter improvement, no Release publication, no Champion/Best promotion. Model 1408 SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` is inherited registry provenance, not independently downloaded or resumed here.
- The Actions Artifact expires; its JSON receipt is committed for long-term handoff. No weight/optimizer ZIP is committed.

## P0 parallel PR audit and integration limits

Read #172 and #177 overlapping guard-alias patches. [PR #172 exact head 4ece91fc](https://github.com/sstxww/reinforcement-learning/pull/172) had true latest-head PR [CI #41510994415](https://github.com/sstxww/reinforcement-learning/actions/runs/41510994415) completed/success, baseline seed 99412 full game [#41510277587](https://github.com/sstxww/reinforcement-learning/actions/runs/41510277587). Posted [comment](https://github.com/sstxww/reinforcement-learning/pull/172#issuecomment-6586758577) advising one selected integration, no duplicate blind merge. The coordinator lease [state file](https://github.com/sstxww/reinforcement-learning/blob/coord/autotavern-main-integrate/coordination/merge_lease.json) states that a concurrent merge occurred during a held lease, so no verifiable global exclusivity was obtained; no PR merged by this session.

## Reproducibility / next round

`python -m pytest -q tests/test_release_step_audit_s_f2a75c38.py tests/test_model_registry.py`

For a *downloaded* Release model whose actual bytes, original metadata and registry are separately trusted:

`python -m tavern_ai.release_step_audit_s_f2a75c38 --model-id <registered-id> --checkpoint <downloaded-model.zip> --metadata <downloaded-model.metadata.json>`

This read-only audit cannot prove optimizer continuity. Next hypothesis for an explicitly-budgeted independent model evaluation: compare verified Release checkpoint under raw PPO action loop vs matched baseline seeds, refuse rank for unfinished game; don't spend new PPO steps merely to paper over rank-eight no-BUY loops. Next integrator action: review non-Draft PR's current source diff/head and merged-main CI under truly exclusive merge queue.
