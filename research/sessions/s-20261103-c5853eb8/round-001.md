# V7 round 001 — serialized integration safety before concurrent merge

SESSION_ID `s-20261103-c5853eb8` / TASK_KEY `infra/v7-serial-integration-gate` / start main `3a745c6f6a48c65528bcbeb81b8627b8db93f046`.

## Hypothesis
With 10–20 simultaneous conversations and an unprotected main, simply checking an old green PR badge allows stale-base or stacked PRs into main. A fixed Actions concurrency group plus fail-closed exact-ref, independent-review, full-match-head gates can reduce cooperative integration races. This does **not** establish a global lease against direct admin API writes.

## Real actions
- Searched and read latest V7 TXT (32,014 bytes) and main AGENTS.md / session rules; inspected open PRs, main CI, registered 1,408-step unpromoted Release and overlapping candidate work.
- Created isolated branch `agent/s-20261103-c5853eb8/optimization-001` from main SHA `3a745c6f6a48c65528bcbeb81b8627b8db93f046`.
- Implemented a Python integration validator with explicit exceptions for non-main PR bases, stale heads, unknown mergeability, changed main, unapproved head, absent exact PR CI and missing full eight-seat job proof.
- Wrote 16 deterministic local regression cases; all passed. Synthetic tests prove only local gate logic.
- Added proposed manual-only serialized Actions integration workflow and independent read-only 55-minute bounded real-game proof workflow. The latter triggered https://github.com/sstxww/reinforcement-learning/actions/runs/41512112571. Its live outcome must be checked.
- No change to public trainer, registry, model, Arena or other workers' PRs.

## Observed P0 blockers
PR #15 is stacked on #9 rather than current main. #165 (Release publish privilege) and #170 (buy probability diagnostics) remain independently owned. Initial main had no branch protection / rulesets, so a single caller cannot infer exclusive global integration rights from its GitHub identity. Workflow must itself enter main, pass review, and be used by all co-operating agents.

## Model and match accounting
PPO steps added here = **0**. No candidate weights, optimizer SHA or durable model released. Full-game proof run `41512112571` is baseline-only seed 93493 seat 0; no placement is claimed until authenticated original receipt is read and verified. No raw/guarded model strength comparison, no Best/Champion promotion. Model source currently registered: 1,408 steps, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; no new resume test.

## Next
Inspect workflow job and Artifact. If successful commit validated original JSON; run PR CI on latest head and current main, obtain independent review before enabling merged workflow on main. Then future integrator can use workflow_dispatch with expected PR head, main head and CI run ID. If any gate fails, classify and record the exact error instead of force merging.

## Later authenticated result
- Own run [41512112571](https://github.com/sstxww/reinforcement-learning/actions/runs/41512112571) completed SUCCESS: pinned actual eight-seat TavernGym 1.1.0 baseline seat 0, seed 93493, rank 5, turns 13, decisions 50, placements [5,1,8,3,4,7,6,2], no truncation. Raw original receipt committed at `experiments/s-20261103-c5853eb8/001-93493.json`; SHA256 `1edd45bf6270122e08c14d169f05cde693614a6ea2ec07d91a2526b2c50f0e10`.
- Examining actual run metadata revealed a dangerous stale-head false positive: run `head_sha` can be older than PR association's head. Commits `ffca08d5` and `fe58b07e` require the run's own executed SHA and recorded main base. 17 local synthetic pytest regressions PASS.
- Non-Draft PR https://github.com/sstxww/reinforcement-learning/pull/190 opened; latest-head PR CI / independent security review / exclusive integrator still required. No PPO steps or new Release; only baseline proof.
