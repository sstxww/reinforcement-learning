# s-20261102-73729553 — R001 state

- Independent branch: agent/s-20261102-73729553/optimization-001.
- Starting main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
- Exact succeeded private run: https://github.com/sstxww/reinforcement-learning/actions/runs/41420333302.
- Evidence commit: 5317dd6aaf3cbb41ce0fed87062ef039548acca4 (later doc commits add the review record).
- Code: tavern_ai/bc_probe_73729553.py; workflow: .github/workflows/bc-probe-s-20261102-73729553.yml.
- Actual training: 250 masked BC updates, 129 train samples/3 complete training games; 0 PPO steps.
- Independent teacher validation: 94 samples/2 games, 95.7447% family accuracy.
- Pure learner canary: experiments/s-20261102-73729553/001-bc_category-67029.json, completed at seed 67029; 8th, zero extra guard.
- Paired seeds 67030-67032: BC [7,8,8], Baseline [8,8,8], insufficient n=3 for strength claim.
- Policy JSON: reports/s-20261102-73729553/001-checkpoint.json; SHA256 ef09f865cbff3fe4b8685df77636045f8886264376dfd6660ff9355591a31ee2.
- Summary: reports/s-20261102-73729553/001-results.json. Seven durable full-game receipts, 12 real full games in action execution including data collection.
- Full checkpoint reload replay: NOT YET independently verified. Champion unchanged. PROMOTION: RETEST only.
- Next: independent model reload verification; then stronger public-observation buy/end teacher, with distinct seeds. Reproduce experiment via python -m tavern_ai.bc_probe_73729553 after engine bootstrap; no scheduled background agent.
