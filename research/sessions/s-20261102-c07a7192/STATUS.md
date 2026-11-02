# s-20261102-c07a7192 STATUS — R001 verified workflow outcome

- Branch: `agent/s-20261102-c07a7192/optimization-001`; PR: https://github.com/sstxww/reinforcement-learning/pull/123 (**Draft**).
- Initial main HEAD: `db5e23ae8c218808821327d806b05d2604cfadfb`; main moved concurrently to `ef77ae6bc5d9bef09e903fac7705917ec3b7366d` at PR creation. Recheck main before merge.
- P0 inventory at start: 75 open PRs, 74 Draft; only non-Draft #15 targets non-main branch. **0 PRs merged by this session.** Specific overlap review recorded on PR #93.
- P1 code: fail-closed two-asset registered Release recovery, SHA256/ZIP/optimizer/engine checks and CPU inference, branch-only train.yml proposal and offline regression tests.
- Actual isolated Actions **SUCCESS**: https://github.com/sstxww/reinforcement-learning/actions/runs/41450150026; source HEAD `2f83885866139d297f4b8ff36489f563d061c894`.
- Real baseline eight-seat receipt: `experiments/s-20261102-c07a7192/001-76012.json`, seed 76012, rank **8**, 15 turns, 30 decisions, `completed=true`, no truncation.
- Registered V5 experimental parent Release: `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; actual download+both asset SHA+ZIP+CPU inference gates succeeded.
- **Actual PPO training this session: 128 additional steps**; cumulative **1408 → 1536** and resulting model SHA256 `c1851820a7cbd353b8d8c91b4a446c512c4f6ba3f7048259da3f61ad932be0d1`. Model-only complete eight-seat game seed 76013, **rank 8**, 16 turns, 122 decisions, no truncation. Genuine validated receipt `experiments/s-20261102-c07a7192/002-76013-model.json`.
- Compact real metrics report: `reports/s-20261102-c07a7192/001-release-resume.json`. New 1536-step weights preserved only in **30-day Actions diagnostic Artifact**, not durable registered Release; do not misstate them as permanently saved. Original durable V5 1408-step parent remains unchanged and recoverable.
- **No paired candidate improvement verified. No Champion or Best. No bulk PPO expansion, no ranked Arena.**
- P2 verified contextual evidence: V5 1408-step policy 35 legal BUY states/0 buys in a main-branch real game; V2 two-game probe 74 legal BUY states/0 buys, 222/248 Refresh/Freeze. Draft #107 negative forced-BUY ablation still rank8 in three small-seed pairs, not yet integrated. Root of learned behavior remains unknown.
- P1 remaining risk: main scheduled train.yml after our proposed change still only uploads **expiring** new outputs and repeatedly evaluates identical seeds; maintain manual small-gate until durable new checkpoint publishing and heldout diversity are fixed.
- Integration gate: final HEAD PR CI must pass with both genuine receipts, concurrent main recheck and integrator ownership before any merge. Do not claim R001 merged.
