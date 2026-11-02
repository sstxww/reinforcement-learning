# Session status — s-20261102-c097d0cc

- Round: 001 (completed real paired evaluation)
- Branch: `agent/s-20261102-c097d0cc/optimization-001`
- Base commit: `6ac59235b8238196a0e6462de77b72413c829372`; experiment run commit: `2fbf7f686edeaf9a64f6c2a10fb849937ddc74a4`
- PR: https://github.com/sstxww/reinforcement-learning/pull/11 (draft, do not merge unverified candidate).
- Algorithm: rightmost legal Play insertion for first baseline-selected hand slot (deterministic rule, no model).
- Completed optimizer/PPO steps: **0**; actually completed 40 full TavernGym games (20 control + 20 candidate).
- Verified candidate mean rank: **7.050** across 20 seeds (first seat rank **8**), no significance claim.
- Model checkpoint: **none**; restoration: run `python -m tavern_ai.placement_probe --agent-id s-20261102-c097d0cc --seed-start 31001 --games 20` after engine bootstrap.
- Receipts: `experiments/s-20261102-c097d0cc/001-*.json` and `experiments/s-20261102-c097d0cc/controls/*.json`.
- Results: `research/sessions/s-20261102-c097d0cc/comparison.json`.
- Workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41413715459
- Validation split: pilot (4 pairs) candidate-control -1.7500; fresh extension (16 pairs) **+0.3125 worse**; all 20 pairs -0.1000. No reliable gain.
- Next step: independent PR CI on final commit, and conditional/minion-stat placement hypothesis with fresh seeds. Do not promote universal rightmost.
