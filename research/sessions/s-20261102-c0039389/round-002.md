# s-20261102-c0039389 — Round 002: eight-seat sweep on fresh held-out seeds

## Research question
Round 001 showed seed-paired seat 0 `[8,8,8]` versus seat 4 `[7,7,4]` while executing exactly the same original V0 BaselinePolicy (https://github.com/sstxww/reinforcement-learning/pull/44). Is seed-conditional sensitivity also observable over **all eight controlled seats** on completely fresh held-out seeds? This is an engineering audit for a statistically sound model evaluation protocol, not an attempt to improve gameplay by changing seats.

## Source, isolation and predecessor
- Original clean main anchor: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- R002 fork point: own R001 head `31adcfe4589df5a419b8c8ce052019d63c1dbc90`, after successful R001 CI run `41417526101`. This stacked R002 work depends on R001 runner implementation; keep PR44 under independent review and **do not merge R002 ahead of R001**.
- Dedicated branch: `agent/s-20261102-c0039389/optimization-002`. No changes to other sessions, shared policies, main training workflow or upstream TavernGym.
- New module `tavern_ai/seat_sweep_experiment.py`, targeted tests and finite branch-specific workflow. Reuse the directly verified real engine `seat_position_experiment.play` from prior round.

## Experiment protocol
- Actual single-seat TavernGym 1.1.0 engine; verify fingerprint `6d8712c93022ba11`, observe2 4017/447/245.
- Independent mandatory canary: controlled seat 7, seed `45720`, receipt `experiments/s-20261102-c0039389/002-45720.json`.
- Fixed held-out seeds `45721,45722,45723,45724`: each one is replayed with an untouched BaselinePolicy controlling each seat in 0..7 while the other seven use official bots. This is 32 genuine complete real games in eight independently seed-paired arms, plus the mandatory R002 canary: **33 total**.
- Validate for every game: `Game.is_over()`, all eight rank placements, own seat/rank match, 0 illegal moves, 0 combat truncations and no safety guard.
- Quantify per seat the actual four ranks, average, top-four and first-place rates; per seed all eight ranks, distinct count and range; paired mean delta against seat 0. Results to `reports/s-20261102-c0039389/seat-sweep-r002.json`.
- **No PPO steps** (`0`); original baseline SHA256 and engine fingerprint in each actual receipt; no new model/checkpoint/Best.

## Interpretation boundary
Changing controlled seat also changes assigned heroes, opponents, turn schedule and possibly RNG trajectory. Any variation only establishes **seat-conditional evaluation sensitivity** under observed seeds and does not prove universal seat advantage, causal mechanism, or a better agent. Four seeds are exploratory; no statistical promotion or best-model update.

## Real evidence
**Pending actual R002 Actions run.** Do not invent run ID, placement, canary success or CI before completion. If failure occurs inspect real job logs, fix root cause and rerun at most twice with substantive corrections.

## Next
If new seeds show substantial seat differences, propose a model assessment gate averaging over multiple controlled seats and independent seeds, separate from trainer changes and Arena play.
