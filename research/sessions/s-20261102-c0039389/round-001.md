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

## Real execution evidence
**Pending**. No run link, completed match, seed-based ranks, performance metrics or check-point hash should be claimed until GitHub Actions actually succeeds. On success, inspect the run and receipt files, update this report with factual run URL, final head, canary rank/decisions, other seven placements, 3+3 paired comparison, all safety assertions, and CI.

## Next hypothesis
If seat 0 and 4 differ, test all eight seats over larger independent seeds with hero stratification and explicit sampling uncertainty, separate from actual policy optimization.
