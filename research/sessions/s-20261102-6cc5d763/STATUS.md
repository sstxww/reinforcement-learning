# Session status — s-20261102-6cc5d763

- Active status: **two complete independently executed strategy ablations; no statistically demonstrated improvement**.
- Round 001 branch `agent/s-20261102-6cc5d763/optimization-001`, draft [PR #27](https://github.com/sstxww/reinforcement-learning/pull/27). Seven full games, zero refresh activations, paired candidate/control [8,8,8]. Workflow [41415018609](https://github.com/sstxww/reinforcement-learning/actions/runs/41415018609) success.
- Round 002 branch `agent/s-20261102-6cc5d763/optimization-002`, draft [PR #33](https://github.com/sstxww/reinforcement-learning/pull/33), source SHA `424edaa91f6a7b7257946dfcd2b82cfebf2267bc`, evidence SHA `af075f4419a73b5097bf1fba793a90c9a36c9e4a`.
- Both branches based on explicit main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`; R002 source/workflow isolated from R001 and other sessions.
- Real Round 002 Actions: https://github.com/sstxww/reinforcement-learning/actions/runs/41415776708, success. TavernGym 1.1.0 hash `6d8712c93022ba11`.
- Mandatory R002 game seed 36511: 8th, 43 decisions, 5 refresh actions, completed; receipt `experiments/s-20261102-6cc5d763/002-36511.json`, no engine safety termination.
- R002 heldout seeds 36512–36515: baseline [5,8,7,8] vs candidate [7,8,2,8], means 7.0 vs 6.25. Candidate top4 1/4, first 0/4. **No proven gain** with n=4.
- R002 saw **32 actual refresh actions across 5 candidate matches**. Policy SHA256 `8af4b69abc82f6c7edc415352f23a73a7a502725cdaa1bbd7129b8b2527fd010`.
- Actual report `reports/s-20261102-6cc5d763/round-002.json`; match receipts `experiments/s-20261102-6cc5d763/`.
- Total independent real eight-seat matches: **16** across the two rounds (R001 7 + R002 9).
- PPO gradient steps 0; this research chose rule-tuning, no model produced. Best and Latest remain unchanged by session. No continuous neural checkpoint to restore.
- Artifact R001 `13127905152` and R002 `13127208879`, both expiring 2026-12-02; not permanent checkpoints.
- Failure analysis R001: [zero activation in PR #27](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-6cc5d763/optimization-001/research/sessions/s-20261102-6cc5d763/failures/001-zero-activation.md); R002 runner had no fatal failure.
- Await review and latest-head CI gate on both draft PRs. Do not auto-merge.
- Next research: >=16 new paired seeds to test R002's fragile mean-rank effect. Stay entirely outside ranked TavernArena.
