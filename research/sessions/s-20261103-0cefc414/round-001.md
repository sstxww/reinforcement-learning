# R001 — bounded concurrent Actions capacity preflight

Hypothesis: with 10–20 sessions, absent even a read-only admission preflight, many costly or redundant workflows can be queued together; a fail-closed snapshot and explicit advisory cap can prevent an individual cooperating caller from launching another when capacity is already exhausted.

Implemented a stdlib-only, read-only GitHub Actions status inventory across queued/in_progress/waiting/requested/pending/action_required. Reject missing/partial status pages, identity errors and invalid thresholds; detect named training-heavy runs conservatively. It deliberately does NOT acquire slots, lock main, claim guaranteed global quota, dispatch or cancel runs. Only cooperative callers can use it as a first preflight, followed by GitHub concurrency protection, exact-head CI and real global budget enforcement where available.

Actual fixed-seed TavernGym baseline run is separately configured for Actions, seed 99697. Receipt, placement, engine contract, run, and elapsed time remain unknown until actual completed logs/artifact are inspected. No model was trained or evaluated, no candidate was archived or promoted. Historical raw PPO rank-8 evidence is not confused with this infrastructure baseline.

Evidence to append: exact branch commit, complete test result, Actions run/jobs/receipt, PR latest HEAD CI and main compatibility. An exact scope-limited independent PR can then be reviewed. No merge without globally enforced exclusive entry (issue #182).
