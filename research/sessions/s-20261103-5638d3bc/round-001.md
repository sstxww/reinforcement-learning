# s-20261103-5638d3bc R001 — matched-seed raw-1408 model probe
Hypothesis: the existing 1408-step unpromoted raw PPO still underutilizes actions and ranks poorly on a new independent seed. A single completed pair can test reproducibility of rank-eight symptoms, not prove the cause or gain.

Historical source: PR #168 seed 99385, baseline 7 vs raw model 8; main registered Release SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632, no Champion. Other sessions already own training workflow, serial integration and Release race fixes, so this task changes none of those files.

Actual configuration: GitHub Actions on own branch, pinned TavernGym 1.1.0, seed 1256380, seat 0, 7 native scripted opponents, source Release downloaded and verified via release_restore_entry, raw unguarded canary, no forced buy, no fallback, no Arena; 45 minute job limit and 15 minute raw-model sublimit. Two full games only if both complete; not a self-play claim.

Before run finishes: new PPO steps 0, new checkpoint/Release 0, completed model games 0, no placement claim. The pushed workflow is an execution request, not proof of a completed game. Original unmodified artifact must be retrieved and committed before any PR is considered ready. Failed/timeout models receive failure status, never invented rank eight.

Integration: this session has only an atomic task claim, NOT the exclusive main integration lease. Do not touch another agent's branch or call merge API without genuine serial authority and latest CI/reviews.
