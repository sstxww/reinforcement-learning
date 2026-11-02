# R001: localize exact failed seed without reclassifying incomplete games

## Source and hypothesis

Read V7 Gmail TXT in full, main `3a745c6f`, docs/SESSION_PROTOCOL.md, docs/CLOSED_LOOP.md, official `tavern_ai/evaluate.py` and `tavern_ai/canary.py`. An existing real training failure in #165/run 41509707315 showed a 1536-step raw candidate could finish seed 932031 at rank 8 but a later two-seed held-out batch raised `Full-game safety limit exceeded` without recording which seed failed. The **specific root cause of the model loop is still unknown**. The verified instrumentation gap is that bulk-list evaluation only returns a report after all runs finish, so a thrown exception discards that call's per-game progress.

## Independent repair

Added `scripts/v7_seed_isolation_d2f99825.py` with one-seed-at-a-time raw canary calls; a file is atomically written after every success/failure; each arm is distinguished; paired scores ignore incomplete arms; model SHA/seed/engine/seat/guard checks are fail-closed; no automatic retries or interventions. If a model arm fails, the independent baseline on that same seed still runs. Wrote eight synthetic tests, all passed locally. No edits to active public training/evaluation/registry modules.

## Immutable facts and limits

- Environment contract TavernGym 1.1.0, source 6d8712c93022ba11, observe2 4017/447, mask 245.
- Known unpromoted parent Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617 / SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632. Not actually loaded by this session.
- New training steps: **0**. Candidate weights/optimizer: **none**. Independent full-model games: **none**. No strength claim, no candidate promotion.
- Own read-only baseline full-game seed: 99437, seat 0, seven scripted TavernGym bots. Actual rank/turns/decisions **unknown until Actions completes**.
- Global task lock: not guaranteed; own uniquely named paths only. No integrator-exclusive lease.

## Falsification and handoff

Run the script against one **verified and downloaded** raw checkpoint for seeds previously known to hang, preserving failure JSON, model SHA and any successful receipts. A safety-limit failure remains a **noncompleted game**, not rank 8. Compare only independently paired complete seeds, then instrument actions/observation transitions around the failing seed. Do not scale PPO based on this failure-localization engineering tool alone.

Next: inspect exact workflow run/job, commit its authentic completed receipt or a separate failure record, open PR, check latest-head CI and hand off merge.
