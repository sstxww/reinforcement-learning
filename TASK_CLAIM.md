# V7 task claim — registry/resume-provenance
SESSION_ID: s-20261103-6c48b19e
TASK_KEY: p0/registry-resume-claim-consistency
ROLE: REPAIRER / REVIEWER (NOT INTEGRATOR)
ROUND_ID: 001
BASE_MAIN_SHA: c1b828734527bae6141805581693d890cc3bff94
OWN_BRANCH: agent/s-20261103-6c48b19e/optimization-001
OWNED_PATHS:
- scripts/v7_registry_resume_claim_gate_6c48b19e.py
- tests/test_v7_registry_resume_claim_gate_6c48b19e.py
- .github/workflows/v7-registry-resume-6c48b19e.yml
- research/sessions/s-20261103-6c48b19e/
- reports/s-20261103-6c48b19e/
- experiments/s-20261103-6c48b19e/
STATUS: claimed
NON-GOALS: no shared train.yml edits; no model promotion; no direct main push; no claim to exclusive merge authority.
CLAIM_HANDOFF: Owner may mark this task complete after one original real eight-seat baseline, full CI and PR handoff; other sessions should choose different files. Branch creation alone is not an integrator lease.

VERIFIED_HANDOFF:
- TASK_STATUS: ready_for_integration; the execution claim is now **released for review/handoff**, no active owner write in progress. This branch is a deterministic task-claim record, never an exclusive main merge lock.
- PR: https://github.com/sstxww/reinforcement-learning/pull/200 (ready, non-Draft)
- PR_HEAD_SHA_AT_HANDOFF: 6fe35000a56b8590d7e45c25e080ee41f0018566
- ORIGINAL_RUN: https://github.com/sstxww/reinforcement-learning/actions/runs/41512975850 COMPLETED SUCCESS, original true baseline eight-seat and audit tests.
- ORIGINAL_GAME_ARTIFACT: https://github.com/sstxww/reinforcement-learning/actions/runs/41512975850/artifacts/13173872617
- OWN_GAME_RECEIPT: experiments/s-20261103-6c48b19e/001-99573.json (baseline rank 7, seed 99573, no raw PPO strength evidence).
- CURRENT_PR_CI: https://github.com/sstxww/reinforcement-learning/actions/runs/41513969882 (queued at initial handoff, inspect conclusion on exact HEAD).
- MERGE: **NOT PERFORMED**. No exclusive serial integration lease acquired by this session, so no main write/merge. Integrator must inspect current main and latest PR CI before any expected-head merge.
- NEW_PPO_STEPS: 0; NEW_MODEL_RELEASE: none; CHAMPION_PROMOTION: none.
