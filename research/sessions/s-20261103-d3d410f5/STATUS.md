# V7 session s-20261103-d3d410f5

- **TASK_KEY:** integrate/serialized-reviewed-main-workflow
- **ROUND:** 001; **ROLE:** P0 REPAIRER / REVIEWER
- **State:** running, no exclusive main-merge lease. Atomic task claim `claims/v7/serialized-main-integrator` is NOT permission to merge.
- **BASE_MAIN_SHA:** 3a745c6f6a48c65528bcbeb81b8627b8db93f046
- **Work branch:** agent/s-20261103-d3d410f5/optimization-001
- **Code:** `scripts/v7_serial_integrator.py`, `tests/test_v7_serial_integrator_d3d410f5.py`, main-only manual workflow `v7-serialized-integrator.yml` with separate read-only preflight and write-scoped merge jobs. Five isolated regression tests passed in Actions #41512407251; latest PR HEAD CI remains unverified until finished.
- **Source reuse:** #117 registered Release resume, #125 staged SHA, #161 fail-closed trainer, #166 failed-publish custody, #169 action telemetry, #176 raw rank-eight evidence (merged concurrently after this session's claim).
- **Model custody:** official registered latest unpromoted V5 1408-step Release `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. No checkpoint loaded by this session.
- **Training:** +0 PPO steps; no new weights; no optimizer resume; no Release publish; no Best or Champion promotion.
- **Authentic game:** COMPLETE SUCCESS (baseline-only, NOT model) in [Actions #41512407251](https://github.com/sstxww/reinforcement-learning/actions/runs/41512407251), pinned TavernGym 1.1.0, seed 99673, seat 0 rank **7**, 43 decisions, 16 turns, eight seats `[7,2,1,3,8,5,4,6]`, no combat truncation/turn-limit. Original validated receipt `experiments/s-20261103-d3d410f5/001-99673.json`, source run head `58073fd1157e84769e9f47bdead39584191216c4`; byte SHA256 `72e4c7094af59f7b2c551c8f5f3f18d6b115fcb36141409bc9fa3cff4655286e`.
- **PR:** #185 https://github.com/sstxww/reinforcement-learning/pull/185, non-Draft. Earlier PR CI #41512555970 failed solely because independent receipt was not committed; 390 passed/1 skipped, exact missing-receipt error. Receipt committed by 1259014683c5bfe834e9cfa8dfeba51419c390f4; latest PR CI pending. **Merged by this session:** none. Main CI #41510861696 succeeded for old `c5edec2e` only.
- **Safety caveat:** GitHub Actions `concurrency` serializes *cooperating* dispatch workflows only. Raw API merges by other sessions bypass the lock. Queue is not a globally enforced integration entry until adopted by every integrator or branch protection is imposed.
- **Release/Model:** none in this task. **Next:** check latest #185 exact HEAD CI and current main SHA; obtain independent GitHub review, establish universal entry adoption/real queue before any merge, then run manual preflight; never treat task claim as merger lock.
