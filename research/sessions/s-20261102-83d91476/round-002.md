# s-20261102-83d91476 R002 — falsifiable Refresh/Freeze -> BUY decision override

## Proven mechanism
- R001 real V2 PPO: 74 BUY-legal exposures, 0 BUY, actions 1+2 were 222/248 total; two ranks 8.
- Pinned upstream `crates/taverngym/src/actions.rs` establishes 1 Refresh, 2 Freeze, 8..15 Buy; `recruit.rs` confirms Freeze toggles shop frozen state and Refresh can spend resources.
- This experiment isolates a single question: if model proposes Refresh/Freeze while BUY is mask-legal, does replacing the action with a legal BUY improve immediate economic behavior and heldout placement?

## Controls
- Read-only immutable V2 Release `v2-learning-41413557445`; SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`; pinned engine verified.
- 4 independent new seeds 45113..45116, same seat-0 and same seven scripted opponents. Every seed: raw frozen V2, V2+exactly-one-style explicit first-BUY override, and original BaselinePolicy.
- The model wrapper records all overridden actions; **override results are not pure PPO**, even when all games complete. Baseline is a descriptive anchor, not teacher training.
- Training steps: 0. Changed model weights: none. No signed Arena or other-agent changes.

## Execution / interpretation
- Run branch-only finite workflow `.github/workflows/buy-override-s-20261102-83d91476.yml`; CI and real data must be inspected before final conclusions.
- Negative or inconclusive placement does not invalidate mechanistic finding; keep both.
- Four seeds are exploratory, not conclusive strength evidence; do not promote Champion or claim a model-level win.
- Dependent stacked PR on own R001 PR #90; do **not** merge R002 separately before #90.
