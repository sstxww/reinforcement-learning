# V5 integration session s-20261103-c1452513

- Session branch: agent/s-20261103-c1452513/optimization-001
- Base main: 3297987e2721cb5e958a6711890be24d036d512b.
- P0: PR #116, #154, #117 were merged by *other* independent sessions; no such merges are attributed to this session.
- P1: patch proposed to split training and releasing. Training and its dependencies now have contents:read, Release publisher alone has contents:write and depends on successful training/evaluation. Source restore remains strictly registered Release only, manual bounded continuation. Added parent/candidate weight SHA256 and step-lineage staging.
- P2: from PR #154 independent authentic full-game Action 41450329264, V5 1408-step raw candidate seed99231 rank8, 38 mask-legal BUY exposures but 0 buys, 70 FREEZE and 42 REFRESH of 122 decisions. No fallback. Draft #107 reports forced BUY alone did not improve 3 observed ranks; Play/Cancel loops remain a hypothesis, not a proven sole cause.
- Own genuine separate pinned-engine eight-seat baseline game **completed successfully** in Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41508962915; seed 932019, seat 0 rank 8, 14 turns, 38 decisions, placements [8,7,4,5,3,1,2,6], no truncation or forced end. Exact source receipt committed: experiments/s-20261103-c1452513/001-932019.json. This proves engine infrastructure only, not candidate strength. No new PPO weights or Champion promotion claimed. Latest exact-head PR CI pending.
- Merge gates: own real complete eight-seat receipt, latest-head CI, concurrent main recheck, no overprivileged training job. Even after merge, actual production Release publication/download validation requires a separate real run.

## Actual bounded PPO continuation and fail-closed evaluation (2026-11-03)

- Action https://github.com/sstxww/reinforcement-learning/actions/runs/41509707315 executed a genuine registered, hashed, CPU-loaded 1408-step V5 Release -> 128 additional MaskablePPO steps -> 1536-step candidate. Source SHA a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632; new candidate SHA b2b4a1039ca0f5c0e8475646c80996601d26efd081be533972638607c277508d.
- Parent 1408 pure-model heldout seeds 932040/932041 had placements [8,8], paired baseline [6,8]. Source report reports/s-20261103-c1452513/001-parent-paired-932040.json.
- Candidate 1536 raw model completed authentic eight-player seed 932031 rank8, 18 turns, 114 model decisions, no truncated combats. Source receipt experiments/s-20261103-c1452513/002-model-932031.json.
- **FAILURE:** candidate heldout evaluation on planned 932040/932041 aborted with RuntimeError: Full-game safety limit exceeded, before an evaluable pair report could be produced. The failing seed within the batch was not logged, and no candidate heldout rank is claimed.
- Consequently the write-only Release publish job was skipped. The failed-run artifact 13171404727 contains source evaluation JSON, candidate full-game receipt and candidate metadata but **not** the candidate model.zip; therefore these new weights are **not durable** and are NOT ready for promotion. This loss motivates adding a separately quarantined temporary failed-weight Artifact to the production train workflow (without bypassing publish gates).
- Authoritative JSON report reports/s-20261103-c1452513/002-1536-candidate-heldout-failure.json. No Champion/Best. Stop increasing PPO budget until non-progress decision loops are isolated; never count incomplete heldout as an eighth-place completed game.
