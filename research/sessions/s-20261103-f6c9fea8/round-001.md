# V7 Round 001 — exact current main CI must be independently verified

## Problem and inherited code
The public repo has numerous concurrent branches. A previously successful main CI run at 990acd21 cannot certify a newer main head c1b8287 while its own run 41512315964 is pending. PR #179 focuses stacked PR readiness; this different, independent P0 task checks postmerge main-head CI freshness without changing shared trainer/evaluator/registry.

## Hypothesis / falsifiable check
A green CI result becomes unsafe as integration evidence if its SHA, triggering event, job result, or mandatory full-game step does not match the current main. Check two main ref reads around the run/job snapshot. Reject any gap or changed SHA. Tests simulate stale SHA, a race, pending/failed/cancelled newest run, missing real game step, and a PR event substituted for push. The pure function is read-only and has no merge capability.

## Evidence discipline
Synthetic fixtures do not count as actual games. A self-isolated workflow runs focused tests plus pinned TavernGym one genuine eight-seat baseline match on seed 99713. Its receipt should be read from real logs/artifact and committed unchanged only after run success. No PPO steps, candidate, optimizer or durable Release are produced. Such a baseline game can establish simulator/CI infrastructure, not PPO improvement.

## Integration status / next action
The work stays on its own branch. After real workflow and matching receipt, require exact HEAD PR CI, then independent security/dependency review; no main merge without an exclusive integrator lease. If run fails, record the original first error and perform at most two materially corrected re-runs. Next integrator must read live SHA/run state again before any expected-head merge.
