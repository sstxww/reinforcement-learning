# V5 integration session s-20261103-c1452513

- Session branch: agent/s-20261103-c1452513/optimization-001
- Base main: 3297987e2721cb5e958a6711890be24d036d512b.
- P0: PR #116, #154, #117 were merged by *other* independent sessions; no such merges are attributed to this session.
- P1: patch proposed to split training and releasing. Training and its dependencies now have contents:read, Release publisher alone has contents:write and depends on successful training/evaluation. Source restore remains strictly registered Release only, manual bounded continuation. Added parent/candidate weight SHA256 and step-lineage staging.
- P2: from PR #154 independent authentic full-game Action 41450329264, V5 1408-step raw candidate seed99231 rank8, 38 mask-legal BUY exposures but 0 buys, 70 FREEZE and 42 REFRESH of 122 decisions. No fallback. Draft #107 reports forced BUY alone did not improve 3 observed ranks; Play/Cancel loops remain a hypothesis, not a proven sole cause.
- Own genuine separate pinned-engine eight-seat baseline game **completed successfully** in Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41508962915; seed 932019, seat 0 rank 8, 14 turns, 38 decisions, placements [8,7,4,5,3,1,2,6], no truncation or forced end. Exact source receipt committed: experiments/s-20261103-c1452513/001-932019.json. This proves engine infrastructure only, not candidate strength. No new PPO weights or Champion promotion claimed. Latest exact-head PR CI pending.
- Merge gates: own real complete eight-seat receipt, latest-head CI, concurrent main recheck, no overprivileged training job. Even after merge, actual production Release publication/download validation requires a separate real run.
