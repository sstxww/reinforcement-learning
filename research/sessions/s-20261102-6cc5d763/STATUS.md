# Session status — s-20261102-6cc5d763

## Completed independent rounds
- R001: draft [PR #27](https://github.com/sstxww/reinforcement-learning/pull/27), `agent/s-20261102-6cc5d763/optimization-001`, 7 real games, no refresh intervention, no effect test; [successful experiment](https://github.com/sstxww/reinforcement-learning/actions/runs/41415018609). Latest PR CI [41415918291](https://github.com/sstxww/reinforcement-learning/actions/runs/41415918291) passed.
- R002: draft [PR #33](https://github.com/sstxww/reinforcement-learning/pull/33), `agent/s-20261102-6cc5d763/optimization-002`, 9 real games with 32 candidate interventions, four heldout pairs baseline mean 7.00 vs candidate 6.25; no proven gain; [successful experiment](https://github.com/sstxww/reinforcement-learning/actions/runs/41415776708) and latest PR CI [41416232307](https://github.com/sstxww/reinforcement-learning/actions/runs/41416232307) passed.
- R003: draft [PR #42](https://github.com/sstxww/reinforcement-learning/pull/42), `agent/s-20261102-6cc5d763/optimization-003`, no policy change from R002, 33 real games with 93 refresh interventions, **16 new heldout pairs**. Successful action https://github.com/sstxww/reinforcement-learning/actions/runs/41416484290.
- All three branches based on explicit main SHA `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`. Only session's own experimental source/tests/workflows/results/proposals modified. No main/upstream/other-agent writes.

## R003 results
- Mandatory model-free candidate game seed **36520**: complete, rank 7, 79 decisions, 15 turns, 7 refreshes; receipt `experiments/s-20261102-6cc5d763/003-36520.json`.
- Evaluation seeds 36521-36536: baseline mean 7.50, candidate mean 7.25, first place 0% both, top-four 0% vs 6.25% candidate. Paired bootstrap 95% CI [-0.875,0.3125] includes zero.
- Candidate policy matches R002 exactly: SHA256 `8af4b69abc82f6c7edc415352f23a73a7a502725cdaa1bbd7129b8b2527fd010`; engine TavernGym 1.1.0 hash `6d8712c93022ba11`.
- Full report: `reports/s-20261102-6cc5d763/round-003.json` and `research/sessions/s-20261102-6cc5d763/round-003.md`.
- R003 model/training: **0 PPO gradient steps**, no checkpoint, no Best/Latest promotion. No ranked TavernArena games.
- Evidence commit `15ccfff2df0a6f7db4a2b1843d0d62871c1a2eb9`; Artifact 13128475363 expires 2026-12-02 and is only for evidence, not persistent model storage.
- Entire session: **49 actual complete eight-player TavernGym games**, 20 fresh heldout paired R002+R003 comparisons. No robust strength improvement proven.
- PR #42 latest-head CI still needs checking after updated research summary; remain draft pending review. No auto-merge.
- Next independent hypothesis: card/board-quality-driven buying and refreshing instead of unconditional rerolls; read newly merged GitHub research before resuming.
