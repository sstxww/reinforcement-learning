# s-20261102-e7783c13 / Round 001: bounded P0/P1 integration and evaluation audit

Source: Gmail V5 TXT, 2026-11-02. Repository: sstxww/reinforcement-learning only.

## Current integration inventory (point-in-time)
- Observed main `db5e23ae8c218808821327d806b05d2604cfadfb`, CI run 41432038040 success.
- Queried 75 open PRs, 74 draft. Sole non-draft #15 is stacked on unmerged draft #9; **zero merges** attempted. Neither a draft prerequisite nor safe integration ownership can be bypassed.
- Canonical main registry, strict receipt integrity, released checkpoints and multiple rank-8 diagnostic probes already exist. Reuse rather than duplicate.
- 15 Releases listed; newest tracked latest experimental model is 1408-step `v5-s-20261102-68099929-1408-41428692617`, unpromoted. Heldout candidate ranks [8,8,8] vs paired baseline [6,8,8], no gain; independent optimizer continuation from the newly published tag remains untested.
- Earlier independent studies show PPO legal-BUY missed opportunities and Play/Cancel loops. Correlative behavior evidence is not full causal explanation; our session did not rerun those experiments.

## Concrete change
Isolated read-only `tavern_ai/paired_eval_gate_e7783c13.py` pairs valid, engine-pinned receipts by seed/seat, rejects duplicate/unpaired observations, mixed checkpoint hashes, malformed eight-seat placements, safety guards and fallback-contaminated PPO evidence. Uses main's strict receipt validator, does not write model registry or trainer. Always `promotion_eligible=false`.

## Local evidence and limits
7 synthetic-only unit tests passed in isolated harness using current main receipt validator logic. These are NOT genuine games or strength evidence. GitHub CI and dedicated true-game workflow are required before merge.

New PPO steps by this session: **0**. Real complete eight-seat matches: **0 at commit creation**. No weight saved, no Champion, no main/upstream/Arena actions.

## Next gates
1. Verify exact-head full-match PR CI and separately run isolated actual TavernGym full match; collect/commit its authentic receipt.
2. Integrators: keep #15 behind #9 and review narrowly valuable, nonduplicated release/registry changes.
3. Evaluate raw candidate against baseline with seed/seat pairing and guard contamination prohibited.
4. Verify the newly released latest checkpoint's independent optimizer continuation before any larger training.
## Verified full-match follow-up (2026-11-02 UTC)
- [Actions run 41450007140](https://github.com/sstxww/reinforcement-learning/actions/runs/41450007140): **success**, pinned TavernGym install, 7 own synthetic format tests, and one **genuine complete** baseline eight-seat match.
- Its original artifact ID 13143688148 was downloaded and inspected independently, not reconstructed from a speculative metric. Raw JSON was committed unchanged at `experiments/s-20261102-e7783c13/001-977813.json`.
- Controlled seat 0, seed 977813, turns 14, decisions 38, placements [8,6,2,5,1,3,4,7], no truncated combats, no turn-limit end, engine hash 6d8712c93022ba11. A baseline rank eight is an engineering check, **not a PPO model outcome or strength claim**.
- This session's actual PPO steps = **0**; PPO complete games = **0**; new checkpoint = **none**; Champion = **none**.
- PR full-match CI triggered before receipt commit may have failed the mandatory evidence gate; verify the new post-receipt exact-head checks before review/merging.