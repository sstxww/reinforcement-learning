# V5 s-20261102-8e64a0da — R001 P0 integration, P1 restore smoke and P2 failure triage

## Completed GitHub integration
- Read latest V5 Gmail TXT (27,248 bytes, 953 lines) and the repository rules. Only writable repository: sstxww/reinforcement-learning.
- Initial main db5e23ae8c218808821327d806b05d2604cfadfb, 75 open PRs (74 Draft), no qualified Champion.
- Audited nine files and complete baseline receipt from PR #102, checked exact-head PR CI 41429028420 success, marked it ready, and squash-merged with exact expected HEAD.
- Resulting main 1afd8297e3c661bee3117ac5301b1ca08d64869b; post-merge CI 41449457029 **success**. Own merge count: 1.
- PR #93 is NOT merge-safe: tests hard-code four historical candidates while current canonical registry contains five. Several independent integrators already flagged this; do not overlap their branch.

## P1 evidence and bounded new smoke
- Canonical latest unpromoted Release: v5-s-20261102-68099929-1408-41428692617, 1408 steps, expected weight SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632.
- Existing registry claims Release asset verification but explicitly leaves **independent optimizer continuation from this published V5 Release** untested.
- This branch isolates a one-shot GitHub Actions run to redownload both Release assets, preflight SHA, CPU load, continue 128 PPO timesteps, audit optimizer continuity, attempt unguarded model full game, and store a diagnostic-only immutable prerelease if training and integrity checks succeed. Baseline canary receipt is required; any failed model game is a failure report, never a fabricated completed receipt.
- Do not promote Champion or interpret raw/guarded/fallback game results as equivalent. New PPO steps and new games remain **unverified until the linked workflow completes**.

## P2 source-backed model behavior
- Main registry's 1408-step latest candidate heldout seeds 99125–99127 ranked [8,8,8] while baseline ranked [6,8,8]; no gain.
- Other real-game studies PR #103 and #107 observe V2 skipped masked-legal BUY and showed Play/Cancel loops; forced buys alone (46 in 3 games) left ranks [8,8,8]. Causal contribution to rank remains unproven.
- Strong next experiment: independent opportunity-conditioned counts for BUY, hand-to-board conversions and no-progress loops, plus raw versus fallback labels; not bulk PPO.

No Arena participation, no upstream modification, no direct main push, no claimed strength gain.
