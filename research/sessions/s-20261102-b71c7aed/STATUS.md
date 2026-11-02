# s-20261102-b71c7aed R001 STATUS

- Scope: P0 live integration triage, P1 canonical checkpoint preflight, P2 raw legal-BUY paired diagnosis and 128-step smoke **only if earlier gates pass**.
- Branch: `agent/s-20261102-b71c7aed/optimization-001`; original main SHA `db5e23ae8c218808821327d806b05d2604cfadfb`.
- PR snapshot: 75 open (74 Draft); only non-Draft #15 is stacked on Draft #9; **0 merges by this session**. No direct main/upstream writes.
- Existing durable unpromoted Latest: `v5-s-20261102-68099929-1408-41428692617`; expected SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; no Champion.
- Existing paired heldout latest [8,8,8] vs baseline [6,8,8]. Independently recorded seed 99128 had 35 legal BUY exposures, 0 buys; root-cause hypothesis is legal economic opportunity underuse, not a proven sole cause.
- Code: `tavern_ai/paired_evidence_b71c7aed.py`, test module and unique bounded workflow only; no changes to shared training, policy, registry, CI, other agent work.
- Pure invariant unit tests: **10 passed locally**. Actual isolated cloud run: [41449881452](https://github.com/sstxww/reinforcement-learning/actions/runs/41449881452), initially in progress. Must inspect final run outcome and artifact before claiming complete games, model load/resume or new training.
- New training steps: **not yet verified** (0 claimed). New own game receipts: **not yet verified** (0 claimed). New permanent saved model: none. No Champion promotion, ranked Arena or large PPO job.
- Live run outcomes should be appended in this unique path only after exact logs/receipts are read; preserve failed-gate logs if training blocked.

## R001 genuine cloud attempt #1: failed safely
- [GitHub Actions run 41449881452](https://github.com/sstxww/reinforcement-learning/actions/runs/41449881452) **FAILURE** at exact workflow head `ae9bedf8baba2cc8fe24625297e390a841e8cebb`.
- 10 invariant tests, pinned engine bootstrap and actual two-asset Release download passed; actual preflight reached raw candidate game.
- Actual seed 920011 raw PPO exceeded 250 **own decisions in one turn**, raising `RuntimeError: Too many actions in one turn; no full-match receipt fabricated`. No candidate full game, no 128 PPO continuation, no new checkpoint, no Champion promotion.
- Genuine baseline on seed 920011: rank 8, 41 decisions, BUY 13 out of 21 legal-BUY exposures. Original receipt preserved without identity edit in [artifact 13144047764](https://github.com/sstxww/reinforcement-learning/actions/runs/41449881452/artifacts/13144047764); `agent_id` has `-baseline` suffix and does not count as valid independent PR gate for this session.
- Failure investigation and accepted nonclaims: [failures/001-raw-turn-loop.md](failures/001-raw-turn-loop.md).

## One targeted recovery run
- Updated only session-owned workflow in commit `984b23c00b8a6884e4c6b6e1c748b12561143f5b` to collect non-intervention raw policy action families (capped 320) and independent own-session real Baseline receipt **before** preserving strict candidate/full-game stop.
- [GitHub Actions run 41450837403](https://github.com/sstxww/reinforcement-learning/actions/runs/41450837403) queued when recorded. Treat its outcome as unverified pending actual logs and artifacts. No policy modification, no bounded PPO train if raw policy cannot finish, no ranked Arena.

## R001 second run final, unguarded real candidate failed twice

- [Second real Actions run 41450837403](https://github.com/sstxww/reinforcement-learning/actions/runs/41450837403): terminal **FAILURE** from same strict raw-model safety check after successful original Baseline, bounded forensic, unit tests, pinned engine and Release download. This is a **confirmed candidate noncompletion**, not a CI infrastructure failure.
- Own 100%-authentic Baseline complete eight-seat canary: [experiments/s-20261102-b71c7aed/001-baseline-920021.json](../../../experiments/s-20261102-b71c7aed/001-baseline-920021.json), seed 920021, rank **7**, 71 decisions, 16 turns, no combat truncations; this is **not** model-strength proof.
- Raw PPO telemetry permanently committed: [reports/s-20261102-b71c7aed/001-raw-loop-920011.json](../../../reports/s-20261102-b71c7aed/001-raw-loop-920011.json). Seed 920011: 320 own actions, stop turn 6, 237 actions in that turn; 306 actions in broad `other` bucket, including observed repeating action IDs 1 (refresh) / 2 (freeze) in first 32. 32 legal-BUY exposures, **zero BUY actions**, 0 guard-forced ends. `other` is not exclusively refresh/freeze and no full-game rank exists.
- Exact raw game paired evaluator again raised `Too many actions in one turn`; 128-step extra PPO, model game, model comparison and new durable Release were **not executed**. Cumulative Latest experimental checkpoint remains preexisting 1408 steps, Champion null, **new steps 0**.
- Complete failure report and bounds: [failures/001-raw-turn-loop.md](failures/001-raw-turn-loop.md). The one substantive forensic retry is exhausted; do not repeatedly burn Actions on the same failing SHA/seed.
