# Session s-20261102-c0039389 — STATUS

## Round 001 — completed and validated
- PR https://github.com/sstxww/reinforcement-learning/pull/44 (draft, not merged); isolated branch `agent/s-20261102-c0039389/optimization-001`, final head `31adcfe4589df5a419b8c8ce052019d63c1dbc90`.
- 7 genuine complete real games. Own canary seed 45600 controlled seat 4 rank 4, 67 actions, all 8 placements [3,1,8,6,4,2,5,7]. Seed pairs seat0 [8,8,8], seat4 [7,7,4]. Run https://github.com/sstxww/reinforcement-learning/actions/runs/41416587540 .
- Final-head PR CI verified SUCCESS: https://github.com/sstxww/reinforcement-learning/actions/runs/41417526101 .
- Full report `round-001.md`, knowledge proposal `research/knowledge/proposals/s-20261102-c0039389-001.md`.
- No PPO training or reliable candidate model: `0` gradient steps, no checkpoint, no Best promotion.

## Round 002 — underway
- **Status:** `in_progress`, R002 candidate games pending actual Actions evidence.
- **Current branch:** `agent/s-20261102-c0039389/optimization-002`, from our own proven R001 head `31adcfe4589df5a419b8c8ce052019d63c1dbc90`; original main anchor `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **Research hypothesis:** sensitivity observed for seats 0 vs 4 should be measured across *all eight* controlled seats and new seeds, before using single-seat ranks to promote new models.
- **Experiment:** genuine TavernGym 1.1.0 / observe2, unchanged original BaselinePolicy vs seven official bots, independent canary seed 45720 controlled seat 7 and 32 seat-sweep games (seeds 45721-45724 × seats 0..7).
- **Planned original evidence:** `experiments/s-20261102-c0039389/002-45720.json`; 32 receipts `sweep-<seed>-seat<seat>.json`, report `reports/s-20261102-c0039389/seat-sweep-r002.json`.
- **Actions:** new dedicated branch-only workflow to be submitted; never reuse main train.yml or other's artifacts.
- **Training/checkpoint:** no PPO gradient steps (0), no model/checkpoint/Best. Policy code hash unchanged since R001: `e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac`.
- **PR:** to be created for R002 after real canary completion, stacked dependence on R001 PR44 explicitly declared. Do not merge before PR44.
- **Next:** evaluate descriptive full eight-seat outcomes with proper confound caveats; if blocked, record actual logs and fix only our own code/workflow.
