# Round 001 — blocked ready PR is not mergeable-to-main

Session: `s-20261103-183db1dc` | Role: WORKER | TASK_KEY: `p0/stale-ready-pr-base-15`

## Input and baseline

- Gmail: latest **AutoTavern-AI V6.1** message at 2026-11-02 19:21 UTC; full TXT `AutoTavern-AI-V6.1-多会话并发闭环自训练完整提示词.txt`, 22229 bytes, read in full.
- Source main on claim: `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`.
- Engine pinned by main: TavernGym 1.1.0, observe2 4017 floats, 447 cards, 245 masked actions; source hash `6d8712c93022ba11`.
- Registry Latest is unpromoted 1408-step checkpoint; `Best=null`.
- No exclusive INTEGRATOR lease or user role authorization was provided. No merge action allowed.

## P0 duplicate-work audit

Current V5 main already integrated manual-only Release continuation (#117), SHA-bound checkpoint staging (#125), Champion guard (#138), and >100-PR audit (#162), so do not write another competing resume/registry or replace shared workflows. Other sessions have active P1 and P2 Draft PRs.

PR #15 is marked non-Draft, at head `ad1bf93498ab5a310e0f4557dde1df7a97bf85fb` with successful full-match check https://github.com/sstxww/reinforcement-learning/actions/runs/41414124225/job/125173727372, but it **targets agent/learning/v1**, not main. PR #9 (its declared parent) is itself open Draft and non-mergeable. Therefore green CI is not a sufficient main merge gate. These facts were checked through live GitHub PR metadata, not inferred from title alone.

## Falsifiable hypothesis and implementation

Hypothesis: a review gate that checks exact base ref + main SHA + draft + latest-head CI + dependency review will classify #15 as blocked, even though its own CI is green. The code must never merge or mark any model promoted.

- New isolated tool `scripts/v61_pr_base_gate_183db1dc.py`, synthetic regression tests `tests/test_v61_pr_base_gate_183db1dc.py`.
- Unique **read-only** Actions workflow `.github/workflows/v61-pr-base-gate-183db1dc.yml` uses read permissions, fetches LIVE PR 15 and main, asserts a blocked result, and runs an independent original seed-99613 baseline eight-seat game.
- Run URL https://github.com/sstxww/reinforcement-learning/actions/runs/41510253654; pending as initially observed. The artifact is temporary until genuine JSON is committed.
- This is a P0 integration-safety tool, **not** a raw PPO improvement, model training, Release publication, or Arena ranking.

## Outcome and honesty constraints

At this initial commit no verified completed new game receipt is claimed. Actual new PPO steps = 0; model SHA/Release = none; model game completion = 0; baseline seed 99613 planned in a running cloud job, not yet reported as done. No files are put under `experiments/` until genuine result exists.

If the run fails, read the actual job step/log, preserve the failure URL and a scoped correction. If it passes, record authentic baseline rank/turns/placements, commit receipt and live gate findings to this branch, and offer a Draft PR with exact CI link. Future P1 raw PPO and custody experiments remain owned by other active sessions.

## Next technical question

Can we demonstrate an exact-current-main, non-Draft PR with a completed latest-head CI and independently cleared dependencies without any unmerged stacked base? If so, it can be recommended for INTEGRATOR review, never auto-merged.
