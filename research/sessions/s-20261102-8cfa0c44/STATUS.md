# Session s-20261102-8cfa0c44 — STATUS

- **State:** running_verification (not completed; no outcome claimed yet).
- **Branch:** agent/s-20261102-8cfa0c44/optimization-001
- **Baseline main:** 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
- **Hypothesis:** process-isolated real TavernGym evaluations can increase full-game throughput without changing fixed-seed results.
- **Source:** tavern_ai/parallel_eval.py; tests: tests/test_parallel_eval.py; private workflow: .github/workflows/experiment-s-20261102-8cfa0c44.yml.
- **Real execution:** [Actions run 41416657474](https://github.com/sstxww/reinforcement-learning/actions/runs/41416657474). Final outcome must be checked.
- **Planned experiment:** mandatory seed 28700, then six serial and six process-isolated games on seeds 28701–28706; seat 0 original V0 baseline, other seven seats TavernGym bots. Compare completed receipts and compute games/s.
- **Environment:** pinned TavernGym 1.1.0 / hash 6d8712c93022ba11; observe2 4017 floats, 447 cards, 245 discrete actions.
- **Training:** 0 PPO steps (evaluation infrastructure only); no model weights, checkpoint, model SHA, or Best promotion.
- **Receipts:** experiments/s-20261102-8cfa0c44/ (pending real execution); summary reports/s-20261102-8cfa0c44/throughput-001.json.
- **Evidence durability:** workflow uploads 30-day temporary Artifact; validated compact receipts will be committed to this session branch if job succeeds.
- **PR:** pending; human review/CI required.
- **Potential failure modes:** process startup overhead, native engine process isolation, repository write permission. Do not infer speedup from a queued workflow.
- **Next action:** inspect run result and job logs; diagnose and rerun only after meaningful fix, then record metrics in round-001.md and a session-specific knowledge proposal.
