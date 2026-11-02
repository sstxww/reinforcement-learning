# Round 001 — V7 serialized-integration preflight, s-20261103-0a059dfe

## Inherited state and overlap avoidance

Read entire V7 Gmail TXT (32,014 bytes), then current `AGENTS.md`, `docs/SESSION_PROTOCOL.md`, `docs/CLOSED_LOOP.md`, `prompts/INDEPENDENT_SESSION.md`, release/train workflows, main model registry, PR list, genuine Actions. Claimed unique `integrate/v7-ci-head-gate` through `claims/v7-main-merge-safety-contract`, and isolated own branch from main `3a745c6f6a48c65528bcbeb81b8627b8db93f046`.

Other sessions already own schema-2 trainer (#164), training token privileges (#165), checkpoint pair installation (#175), reward/BUY-loop root-cause studies (#170/#180), and model Releases. We did not overwrite them or launch redundant PPO training. #164 and #165 merged while this session was running; latest checked main `c1b828734527bae6141805581693d890cc3bff94`, corresponding post-merge CI #41512315964 SUCCESS.

## Single falsifiable hypothesis and implementation

**Hypothesis:** a generic green PR check can accidentally be reused even if it comes from a different PR, a different tested main base, an old head, a zero-job run or a skipped true eight-seat step. Such false-positive integration readiness is particularly dangerous under 10–20 simultaneous sessions.

Created `scripts/v7_pr_gate_0a059dfe.py` as a deliberately read-only additional preflight. It requires exact head, correct PR number and tested base SHA, open non-Draft main target, `clean` mergeability, completed successful latest matching PR CI, nonzero complete job list, correct `tests-and-full-match` job and all mandated genuine test/engine/game/artifact steps. It rechecks main for drift. It cannot grant a merge right, approve reviews, or prove the merged tree was tested. Added **10** synthetic focused tests covering green valid preflight vs never merge-authorization, zero-job, wrong head, later failed CI, missing/skipped eight-seat step, incomplete job page, draft, stale main, wrong event, malformed inputs, wrong PR number and old tested main. No result is a synthetic placement or artificial PPO training.

## Real runner

Actual own finite read-only Actions: [#41512239510](https://github.com/sstxww/reinforcement-learning/actions/runs/41512239510) SUCCESS on `c6016d32818c14972b1ccbeef4737c277f813105`. The runner's focused tests (at that historical revision) passed, TavernGym 1.1.0 `observe2` source `6d8712c93022ba11` installed and pinned, and baseline policy completed an eight-seat match seed 96031. Original Artifact 13174640369 downloaded and hash checked: `3161a072588dfb17ec43e86ff1f0720758e427a113b6dc9a2596924a4269db9b`. Original receipt committed to `experiments/s-20261103-0a059dfe/001-96031.json` (completed true, 15 turns, 50 seat-0 decisions, rank 7, permutation [7,3,1,6,4,2,5,8], no truncations or turn-limit end). This evidence is of simulator/test infrastructure, **not** PPO strength. Changes made *after* the standalone Actions run (PR/base CI association tests) must pass new exact-head PR CI before integration.

## PR #175 review (no changes to owner branch)

Examined actual race-safe `os.link` installation patch and synthetic rollback tests. Its completed independent full baseline receipt is seed 94731 rank6; exact-head main PR CI [#41511418837](https://github.com/sstxww/reinforcement-learning/actions/runs/41511418837) passed every job step. Submitted anchored [PR #175 review](https://github.com/sstxww/reinforcement-learning/pull/175) ID 5742331128, noting that two hardlinks are not crash-atomic, Draft state remains, and main drift/integrator gate must be resolved. This is not an APPROVE or merge.

## Model and hypothesis decision

No newly trained model: +0 PPO steps; no new weights, optimizer-state save, Release, Champion promotion or raw candidate complete matches; no paired evaluation. Historical 1408-step Release `v5-s-20261102-68099929-1408-41428692617`, SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, remains experimental, with raw three-seed rank [8,8,8] vs baseline [6,8,8]. BUY=0 amid mask-legal BUY exposures / REFRESH/FREEZE loops are supported symptoms but insufficient to prove one root cause. Next research hypothesis must isolate true raw no-progress action/state transitions instead of merely adding PPO steps. Do not put a rejected or nonfinishing candidate in latest/best/champion.

## Next exact step

Create non-Draft own PR, let fresh exact-head CI run all tests and a second genuine eight-seat independent baseline gate, inspect run/job steps and head/base. Only a separate truly exclusive main integrator under V7 plus actual review/security and tested main compatibility may call GitHub merge API; no such lease held here. After handoff release this claim branch state so next session is not misled.

Fail-safe note: no main direct commits, no Arena, no credentials/weights added, no background self-running promise.
