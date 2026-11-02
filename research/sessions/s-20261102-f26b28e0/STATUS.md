# s-20261102-f26b28e0 STATUS — deduplicated P0 evidence integration

- PR: https://github.com/sstxww/reinforcement-learning/pull/114, modified to preserve only non-duplicate evidence and research handoff after concurrent main integration #140. No second paired evaluator required.
- Current source branch: `agent/s-20261102-f26b28e0/optimization-001`; start main `db5e23ae8c218808821327d806b05d2604cfadfb`. Competitor main advanced during audit, so final CI and merge re-check required.
- Own live workflow https://github.com/sstxww/reinforcement-learning/actions/runs/41449892693 SUCCESS, genuine eight-seat baseline TavernGym seed 65241 seat 0 rank 8, 17 turns, 45 decisions, 0 truncations; receipt `experiments/s-20261102-f26b28e0/001-65241.json`.
- Historical paired 1408-step experimental model: n=3, ranks [8,8,8] vs baseline [6,8,8], +0.667 worse, no Champion promotion; exact generated report `reports/s-20261102-f26b28e0/001-paired-1408.json`. Missing raw/guard attribution so no pure PPO strength claim.
- Initial PR CI https://github.com/sstxww/reinforcement-learning/actions/runs/41449951853 failed only because self receipt not yet in diff. After receipt added, CI https://github.com/sstxww/reinforcement-learning/actions/runs/41450312937 SUCCESS, 246 passed 1 skipped plus full game. Final deduplicated HEAD requires new CI.
- Main already integrated richer canonical comparator via #140. Removed our duplicative comparator/workflow/tests instead of merging two similar tools.
- Unresolved P1 main train.yml lacks durable Release restore on Artifact expiry and silently restarts. No unsafe main trainer changes made.
- This session PPO gradient updates 0, owned model games 0, owned completed baseline eight-seat games 1, checkpoints 0, Arena 0. Not allowed to scale training until P0–P2 gates.
