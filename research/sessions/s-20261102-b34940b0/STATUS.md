# s-20261102-b34940b0 — independent round 002

- Base main SHA: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`; new branch `agent/s-20261102-b34940b0/optimization-002`.
- Relationship: distinct follow-up hypothesis to independently completed [round 001 PR #32](https://github.com/sstxww/reinforcement-learning/pull/32); not a replacement for that PR.
- Hypothesis: global last-option weakness may primarily result from changing initial hero selection. Compare original baseline, all-turn-last-option, and post-opening-last-option on genuine TavernGym, with 8 matched seeds and 24 complete games.
- Training budget: 0 PPO updates; deterministic rule-policy tuning only.
- Runtime, metrics and receipts: pending proof. No performance claim.
- No neural checkpoint; source code is reproducible via commit.
- Main baseline/shared workflows/other sessions untouched.
