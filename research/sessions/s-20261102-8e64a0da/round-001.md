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

## Source-checked P2 diagnostics (existing integrated main, not this session's new games)
- `reports/s-20261102-68099929/003-buy-opportunity.json`, actual genuine seed 99128 / registered 1408-step model SHA a73d24c68...: model 117 decisions, masked-legal BUY at 35 of those, zero actual BUY, rank 8. Same-seed baseline 39 decisions, masked-legal BUY at 21, 14 actual BUY, also rank 8. This confirms opportunity-conditioned purchase omission, **not** that purchasing would by itself improve placement in that seed. Both rank 8, so this is behavioral evidence not rank advantage.
- `reports/s-20261102-ba09e2d4/002-action-opportunities.json`, separate original V2 1280-step model SHA 73bde266...: unguarded seed 87102 failed complete eight-seat game after bounded 6000 decisions; 2978 hero-power and 2977 cancel actions, only 2 END, no BUY, last turn 3. This establishes a severe HeroPower↔Cancel loop in that checkpoint; no match receipt from the unfinished raw trajectory.
- `reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json`: opt-in guarded V2 full games seeds 87102/87103 both rank 8, despite 4/0 guard interventions and no BUY. Same-seed baseline ranks [5,7]. Guarded complete-game ranks MUST NEVER be called raw PPO results.
- Different checkpoints and seeds must be kept separate. These point to a two-stage issue: action selection failure (when buys legal) and nonprogressing choice loops. Inspect reward/advantage, masks, economics and state transitions before making any causal learning claim or expanding budget. Explicit legal-buy override from draft #107 yielded 46 true purchases across 3 games but ranks remained [8,8,8] and Play/Cancel cycles persisted; not a validated strength repair.
