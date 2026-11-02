# Session status — s-20261102-d97f219e

## Current state
- State: `pending_pr_ci`; all six real games + regression tests complete, no model-strength claim.
- Branch: `agent/s-20261102-d97f219e/optimization-001`
- Main base: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Experiment code commit: `7b2c8e07c8112b919e2526728c12dad36fde5dfb`
- Verified evidence commit: `f1d484ec56a2a6825addde46c28ebadada5d71cb`
- PR: https://github.com/sstxww/reinforcement-learning/pull/26 (draft pending latest-head CI)
- **Real GitHub Actions:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415065755 — SUCCESS, 25 tests passed, 6/6 real complete matches.

## Verified result
- TavernGym: 1.1.0; observe2: 4017 floats / 447 cards / 245 legal-masked actions;
  source fingerprint `6d8712c93022ba11`.
- Seeds 36011, 36012, 36013, then reversed; **3/3 exact trajectory SHA-256 comparisons matched**.
- Own actual full-game receipt: `experiments/s-20261102-d97f219e/001-36011.json`
  (seed 36011, seat 0 rank 8, decisions 39, turns 14, placements [8,3,2,4,5,6,7,1]).
- Compact paired metrics: `reports/s-20261102-d97f219e/replay-001.json`.
- First three distinct seeds: ranks [8,7,8], mean rank 7.6667, first-place 0%,
  top-four 0%; small sample and V0 baseline only, not a performance gain.
- 0 invalid actions observed, 0 truncated combats, no turn guard; six games completed.
- The V0 baseline controls seat 0; seven official scripted TavernGym bots
  control other seats. This is NOT PPO model evaluation.
- PPO steps: **0**. Model SHA: none. Best/Candidate/Latest checkpoint: no models
  produced or promoted in this session. No checkpoint restore path.
- Source/results/receipt permanently versioned in GitHub; Action Artifact retained
  for 30 days only, not permanent weights.

## Lessons / next work
- Trajectory-level replay equality is stronger than identical final rank.
- Scope is three seeds, one pinned version, one policy, one platform: do not
  assert universal determinism.
- No experiment incident in this session; historical incident list was reviewed.
- Historical experimental PPO continuation reported no rank benefit (PR #15);
  no checkpoint in this session can supersede its candidate.
- Next hypothesis: order-invariance of independent **paired different policies**
  on held-out seeds (requires separate validation and clear policy provenance).
- Latest PR-head CI must pass before marking completed_for_review; no merge performed.
