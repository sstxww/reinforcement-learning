# s-20261102-c0039389 — Round 001: controlled-seat evaluation sensitivity

## Hypothesis and provenance
The project's `tavern_ai.canary.run` always controls seat 0, and `tavern_ai.evaluate.summarize` reads `placements[0]`. This makes the sample conditional on seat zero. Test whether changing the controlled seat changes observed placement even when strategy code and random seeds are held constant. This checks **evaluation robustness**, not a strategic improvement; different seats may imply different heroes/opponent schedules, so causal seat advantage is not identified.

Base: main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d` (2026-11-02T08:36:36Z). Independent branch: `agent/s-20261102-c0039389/optimization-001`. No upstream writes, no Arena actions. Original policy unchanged.

## Cross-session references examined
- main `research/knowledge/INCIDENTS-20261102.md`: PPO loop / Release permission / assertion mismatch / excessive reruns. Those are historical, not asserted as current.
- Open PR #28 hold-sell: 3 same-seed ranks identical; PR #27 refresh: zero trigger; PR #29 upgrade-before-play: identical ranks after 3 pairs; independent validation matters.
- Open PR #26 trajectory replay specifically audits deterministic event traces, not the impact of who controls which seat; avoid editing overlapping files.
- Multiple active PPO entropy, reward and card embedding experiments were not treated as proven improvements.

## Implementation
New `tavern_ai/seat_position_experiment.py`:
- Real `taverngym.Game(seed=seed)`, one policy-controlled seat (0 or 4), remaining seven seats always upstream `game.bot_play`.
- Real `observe2`, per-seat legal masks and original `BaselinePolicy`, game runs to `game.is_over()`.
- Receipt adds `controlled_seat`, `controlled_rank` and original baseline SHA256. Reject incomplete placement permutations, rank-seat mismatches, illegal actions, battle truncation and safety limits.
- Save a mandatory independent seat-4 full game seed 45600 and three pairs (45601-45603; seat 0 and seat 4).
- Different branch-scoped Actions workflow; one bounded run with no trigger loop, 30-day Artifact plus branch-committed compact JSON.

## Baseline, training and interpretation
Baseline: untouched V0 rule policy controlling seat 0. Experimental arm: the **same** V0 rule policy controlling seat 4. Not a trained PPO candidate. PPO training steps: **0**. No model checkpoint or Best promotion. Both arms share each seed, but distinct seats may receive distinct heroes and action order; any rank difference is descriptive only.

## Real execution evidence (verified)
- Successful isolated run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416587540. Job `125181813694` completed **success**. Workflow trigger SHA `4f775d7edab7114a17a740f864d26777b308c72f`. Evidence bot commit `f201284469f777a9dec0fe80f206a461c9dbb100`.
- The complete repository pytest suite passed, real pinned TavernGym bootstrap and contract passed, **7 independent full eight-seat TavernGym games** passed all validation, and generated data was committed to our session branch.
- Required self-controlled game: `experiments/s-20261102-c0039389/001-45600.json`. Seed `45600`, controlled seat `4`, final controlled rank **4**, decisions **67**, game turns **17**, eight placements `[3,1,8,6,4,2,5,7]`, `Game.is_over()==True`. No invalid actions, truncations (`0`) or turn-limit end (`false`).
- Three untouched control games at seat 0 and three identical-policy experimental games at seat 4, paired by held-out seeds `45601,45602,45603`. Seat-0 ranks `[8,8,8]` vs seat-4 ranks `[7,7,4]`. Mean rank seat0 `8.0`, seat4 `6.0`; paired rank differences `[-1,-1,-4]`, average `-2.0`. Top-four rates `0/3` vs `1/3`; first-place rates both `0/3`. Evidence `reports/s-20261102-c0039389/seat-comparison.json`, each original full receipt under `experiments/s-20261102-c0039389/`.
- Real engine `TavernGym 1.1.0`, fingerprint `6d8712c93022ba11`, observe2 4017 / 447 / 245. Original untouched rule policy source SHA256 `e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac`.
- **Not a gain:** seat assignment may also change heroes, opponents and action order. This small sample establishes seat sensitivity for these seeds, **not** a causal effect or improvement in underlying decision policy. No PPO model was used; training steps `0`, checkpoint `null`, Best/Latest unchanged. No formal inference from n=3.
- Artifact ID `13127922958` expires `2026-12-02T08:57:41Z`; compact immutable evidence is preserved in the branch. No permanent model artifact was created.
- Faults / repairs: none in this experimental run. Final PR-head CI will be reported separately; do not infer PR CI success from this branch's custom workflow.

## Next hypothesis
If seat 0 and 4 differ, test all eight seats over larger independent seeds with hero stratification and explicit sampling uncertainty, separate from actual policy optimization.
