# V5 round 001 — raw PPO public state-transition diagnosis

Session: `s-20261103-71e4c9b2`; branch: `agent/s-20261103-71e4c9b2/optimization-001`; base main SHA `3297987e2721cb5e958a6711890be24d036d512b`.
Research question: are the observed REFRESH/FREEZE decisions visibly changing **public** TavernGym observations (rather than falsely interpreting repeated action labels as no-op loops)?

## P0 integration readback
Before work the parallel integrators merged #116 strict ZIP preflight, #154 pool integrity and raw rank-8 evidence, #125 SHA-bound checkpoint writer, and #117 manual-only fail-closed registered Release source plus durable **unpromoted** output. Shared `train.yml` is already repaired; no duplicate module, main write, Release overwrite, Champion or Arena match.
Other competing continuation Drafts (#110/#123/#147/#149) should not be merged indiscriminately. An independent review of #123 and evidence update on issue #78 were posted.

## Existing actual evidence, not new result
Published V5 1408-step Release: `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Existing authentic raw seed 99231 ranked 8, 42 Refresh / 70 Freeze / 0 Buy in 38 mask-legal Buy decisions, no guard/fallback. No new causal claim and no improvement.

## R001 unique test
New isolated public transition probe `tavern_ai/transition_probe_s_71e4c9b2.py` runs *unchanged raw model only*, observes pre/post feature/card/mask byte equality after real TavernGym actions when the **same seat still acts in the same turn**. Incomparable post-states are excluded, not called no-ops. Bounded at 220 actions on independent seed 99232. No actor interventions, opponent private state or hidden Arena data. Offline action range/byte regression tests in `tests/test_transition_probe_s_71e4c9b2.py`.

An isolated Actions workflow does engine bootstrap, strict Release download SHA check, model-independent baseline full eight-seat game, model raw transition probe, and model-controlled complete game. Results must be read from actual run, not inferred from workflow code. Source code and test are already committed; no claims of new game, PPO training or checkpoint yet. New training steps 0.

## P1 and P2 follow-up
Production main now supports manual verified Release continuation and durable unpromoted publication, but latest-head main CI, actual main-only workflow_dispatch, optimizer continuity and matched heldout quality must be verified before claiming full production execution. This R001 is strictly a **causal diagnosis** step; if post-state byte equality is frequent, the next trial should test just one action-family anti-loop hypothesis with raw/fallback-separated heldout games. Do not force BUY and claim ranking improvement; #107 found forced purchases alone did not fix rank 8.
