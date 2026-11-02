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

## Actual real engine evidence — complete success
- GitHub Actions: https://github.com/sstxww/reinforcement-learning/actions/runs/41418165218, status `completed success` on source SHA `7274a19d2af94e1e1db7568f88cc7024d509b5c1`. The bot committed the generated evidence to `e585cb00863740eadd4a3046ef9a704e17c5f491`.
- Whole pytest suite and exact pinned TavernGym engine/observe2 passed. **33 genuinely complete real eight-seat TavernGym games**, all with `Game.is_over()==True` and validated controlled-seat rank/permutation, no illegal actions, no combat truncation or game limit.
- Independent R002 personal candidate-controlled game: seed `45720`, seat `7`, rank `8`, decisions `34`, turns `17`, placements `[4,5,3,2,7,6,1,8]`; receipt `experiments/s-20261102-c0039389/002-45720.json`. All seven other seats are original TavernGym official bots.
- Held-out seeds `45721,45722,45723,45724`, each run separately across controlled seats 0..7 (32 additional matches). Seat mean placements `[7,5.75,8,7.25,7,7.75,7.25,7.25]`; per-seat ranks:
  - seat 0 `[8,6,7,7]`; first/top4 `0/4`.
  - seat 1 `[8,3,7,5]`; first `0/4`, top4 `1/4`.
  - seat 2 `[8,8,8,8]`; first/top4 `0/4`.
  - seat 3 `[8,6,7,8]`; first/top4 `0/4`.
  - seat 4 `[6,7,7,8]`; first/top4 `0/4`.
  - seat 5 `[8,8,8,7]`; first/top4 `0/4`.
  - seat 6 `[8,6,7,8]`; first/top4 `0/4`.
  - seat 7 `[8,7,7,7]`; first/top4 `0/4`.
- All four held-out seeds produced non-identical controlled-seat ranks; per-seed rank ranges `[2,5,1,3]`. Seat 4 and seat 0 had **equal mean rank 7.0** on fresh seeds, in contrast to R001 seat4 mean 6 vs seat0 8. Hence no reproducible fixed seat4 advantage from these n=4 seed results.
- Full data: `reports/s-20261102-c0039389/seat-sweep-r002.json`, 32 `experiments/s-20261102-c0039389/sweep-<seed>-seat<seat>.json` receipts. Source original V0 baseline SHA256 `e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac`; TavernGym 1.1.0 source `6d8712c93022ba11`; observe2 4017/447/245.
- PPO gradient steps **0**; no new weights/model checkpoint or Best promotion, no Arena matches. Separate 30-day Artifact `13128209144` expires `2026-12-02T09:10:07Z`. Permanent compact provenance and receipts kept in our own GitHub branch.
- **Result:** greater evaluation robustness concern validated for sampled seeds, **not a gameplay improvement**. Changing seat affects game hero assignments and stochastic opponent trajectory, confounding pure seat causation. n=4 independent seeds too small for strong population inference.
- **Fault loop:** no R002 test/game/CI failures in its dedicated Actions workflow; no repair needed. Final dependent PR-head CI remains separate.

## Next
If new seeds show substantial seat differences, propose a model assessment gate averaging over multiple controlled seats and independent seeds, separate from trainer changes and Arena play.
