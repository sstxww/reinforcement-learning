# V5 integration session s-20261103-c1452513

- Session branch: agent/s-20261103-c1452513/optimization-001
- Base main: 3297987e2721cb5e958a6711890be24d036d512b.
- P0: PR #116, #154, #117 were merged by *other* independent sessions; no such merges are attributed to this session.
- P1: patch proposed to split training and releasing. Training and its dependencies now have contents:read, Release publisher alone has contents:write and depends on successful training/evaluation. Source restore remains strictly registered Release only, manual bounded continuation. Added parent/candidate weight SHA256 and step-lineage staging.
- P2: from PR #154 independent authentic full-game Action 41450329264, V5 1408-step raw candidate seed99231 rank8, 38 mask-legal BUY exposures but 0 buys, 70 FREEZE and 42 REFRESH of 122 decisions. No fallback. Draft #107 reports forced BUY alone did not improve 3 observed ranks; Play/Cancel loops remain a hypothesis, not a proven sole cause.
- Current session: no new PPO training, no model weights, no Champion promotion, no Arena games. Own full-game smoke and final PR CI remain pending; this document does not invent a receipt.
- Merge gates: own real complete eight-seat receipt, latest-head CI, concurrent main recheck, no overprivileged training job. Even after merge, actual production Release publication/download validation requires a separate real run.
