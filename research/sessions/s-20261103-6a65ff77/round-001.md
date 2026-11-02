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
