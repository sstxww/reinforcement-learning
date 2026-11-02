# s-20261103-5638d3bc R001 — matched-seed raw-1408 model probe
Hypothesis: the existing 1408-step unpromoted raw PPO still underutilizes actions and ranks poorly on a new independent seed. A single completed pair can test reproducibility of rank-eight symptoms, not prove the cause or gain.

Historical source: PR #168 seed 99385, baseline 7 vs raw model 8; main registered Release SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632, no Champion. Other sessions already own training workflow, serial integration and Release race fixes, so this task changes none of those files.

Actual configuration: GitHub Actions on own branch, pinned TavernGym 1.1.0, seed 1256380, seat 0, 7 native scripted opponents, source Release downloaded and verified via release_restore_entry, raw unguarded canary, no forced buy, no fallback, no Arena; 45 minute job limit and 15 minute raw-model sublimit. Two full games only if both complete; not a self-play claim.

Before run finishes: new PPO steps 0, new checkpoint/Release 0, completed model games 0, no placement claim. The pushed workflow is an execution request, not proof of a completed game. Original unmodified artifact must be retrieved and committed before any PR is considered ready. Failed/timeout models receive failure status, never invented rank eight.

Integration: this session has only an atomic task claim, NOT the exclusive main integration lease. Do not touch another agent's branch or call merge API without genuine serial authority and latest CI/reviews.

## OWN real GitHub Actions result and verified receipt custody
- Run [41513735245](https://github.com/sstxww/reinforcement-learning/actions/runs/41513735245), source commit 59d821ece38ddf1312ffa5473ba7c24bfda692a5, job paired SUCCESS: installation, pinned contract, registered Release download + SHA verification, baseline canary, unguarded raw PPO canary, matched-seed receipt validation, Artifact upload all succeeded.
- Downloaded Artifact [13174089273](https://github.com/sstxww/reinforcement-learning/actions/runs/41513735245/artifacts/13174089273) ZIP SHA256 db237694960aa95a9279588fe58b4d2b3b963128cb65cc68ee780353440b1857, CRC passed. Reconstructed source bytes from exact JSON with git blob identity checks; committed original receipt bytes untouched.
- Original model receipt seed 1256380, seat0 rank 8, all placements [8,6,7,1,5,2,3,4], 15 turns, 151 decisions, completed true, truncated 0, turn limit false, model SHA a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632, SHA256 6d6f614007b454f89f9d1975a4916904a9bb03819039274f3fe6c83070f79667.
- Original baseline same seed seat0 rank 6, all placements [6,2,8,1,5,3,7,4], 16 turns, 71 decisions, completed true, truncated 0, turn limit false, SHA256 7bc8f1725f395114a6127df592ec44e566ed63882583ce2f9a6b309420424997.
- Paired delta model-minus-baseline +2 positions (worse model), **n=1**. No causal/significance claim, no added PPO steps, no new weights or durable candidate Release, no Champion or Best promotion.
- Historical evidence read in separate source reports: 210/233 prior decisions REFRESH/FREEZE across seeds 99231/99384, 0/65 legal BUY decision exposures; these are not NEW games. See reports/s-20261103-5638d3bc/001-source-evidence-synthesis.json.
- Next: open non-Draft PR after committing genuine receipts; require fresh PR-head full-match CI and independent security review; main merge remains blocked without exclusive gateway.
