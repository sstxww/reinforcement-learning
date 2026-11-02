# R001 — V7 main-CI evidence gate, not another competing PPO pipeline

Task `integrate/postmerge-exact-main-ci-evidence`; base `3a745c6f6a48c65528bcbeb81b8627b8db93f046`; role WORKER without global integration lease.

## Inherited, not reimplemented

Read latest full 32,014-byte V7 TXT, `AGENTS.md`, session and closed-loop protocols, official main training workflow, model registry, current Actions/main, PR #179 and #175/#164/#177/#180 scopes. Main already has protected fail-closed manual Release continuation through #117 and prior publisher/model integrity gates; we avoid altering overlapping files. #179 is premerge PR head/base/dependency gate. Our scoped novel feature is **postmerge proof bound to current main SHA**, so green prior-head PR checks cannot falsely mark integration complete.

## Falsifiable hypothesis and change

Hypothesis: a purported successful GitHub CI run with (a) prior main SHA, (b) skipped full-game step, (c) non-push event, or (d) expired/missing receipt evidence must not count as successful *current-main* postmerge validation. Added `scripts/v7_main_ci_verify.py` and synthetic tests. It explicitly does not claim lease ownership, PR merge, model fitness, or that an Artifact contains a parsed receipt.

Local Python tests: `python -m pytest -q test_v7_main_ci_verify_6a65ff77.py` (9 passed in a locally isolated copy). Required cloud execution: unique read-only workflow, finite 45-minute timeout, and own true baseline eight-player TavernGym canary seed 99731 with original receipt uploaded for later verification.

## Unchanged model reality

0 new training steps / 0 candidate PPO matches / no new checkpoint or model Release; official registered 1408-step candidate only as background evidence, not retested. Model candidate rank-eight and BUY/REFRESH/FREEZE behavioral limitations remain unresolved; other active sessions own these diagnostics. Never call a baseline game a raw model match. No Arena, secrets, upstream write or Best/Champion promotion.

## Integration gate and next action

Current main is not branch protected and no verified exclusive integrator lease exists in this session. Do not merge any PR despite green CI. After genuine Actions success, commit authentic eight-seat receipt and live postmerge-audit report, open a **non-Draft** PR and ask the true unique integrator to validate latest HEAD/merged result. If the real game or GitHub Actions is unavailable, label blocked and preserve failure evidence rather than fabricate a match.

## Verified original GitHub execution — 2026-11-03 UTC+8

- Own [Actions run 41512618506](https://github.com/sstxww/reinforcement-learning/actions/runs/41512618506) **completed SUCCESS**, workflow source SHA `7e7efa82be5efa65cf104f69a4dae52b45a79fbc`. 9 focused regression tests, read-only LIVE main check, pinned engine setup, eight-seat baseline canary, and Artifact upload all passed. No training executed.
- Original [Artifact 13174940306](https://github.com/sstxww/reinforcement-learning/actions/runs/41512618506/artifacts/13174940306) downloaded and ZIP inspected. Original `experiments/s-20261103-6a65ff77/001-99731.json` bytes SHA256 `6951858f89790b4207d76c1d6cd7d71e1c3b56b4c3ed4ac8c830f1117479fff1`; seed 99731, `policy=baseline`, seat 0 **rank 8**, complete placements `[8,5,3,7,2,4,1,6]`, 15 turns, 42 decisions, no truncation or forced turn-limit. This is **not** a PPO rank or training-strength result.
- Original `reports/s-20261103-6a65ff77/001-live-main-ci.json` SHA256 `8bd29b579214a162b3a6fa4500df27996da2dc5e4f4683fa52ef45d0228f9c86` faithfully records `blocked`: when audited, exact main `c1b828734527bae6141805581693d890cc3bff94` run 41512315964 was **still not completed**. Do not rewrite this negative historical snapshot.
- Later independent rerun check: that exact main run https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964 became **SUCCESS**; the authentic `ci-full-match.json` from Artifact 13173024502 was downloaded and checked: seed 1001, baseline seat-0 rank 7, completed 16 turns, full places `[7,3,4,5,1,2,8,6]`; source receipt SHA256 `8b49e84d6ff0e1eef771826f8ccb5b4a81d1cf2f9bacf29b842cffbc0bd4ac10`. Own `reports/.../000-independently-verified-previous-main.json` anchors its exact identity. **If main advances, re-audit the new SHA.**
- Model steps added **0**; raw model games **0**; model release produced **none**; known 1408-step registered Release remains external prior history. `best`/`champion` not promoted. No unique integration lease, no PR merged by this session, no main CI claimed for unmerged code.
- Next step: open non-Draft scoped PR with the exact own game receipt and artifacts; verify PR latest-head tests and full-match CI; hand off merge decision to a real exclusive integrator, not an unprotected concurrent caller.
