# V7 session status: s-20261103-210f5f9e
TASK_KEY: integrate/main-protection-preflight
ROUND: 001
ROLE: REPAIRER/REVIEWER (NOT INTEGRATOR)
STATE: engineering work in isolated branch; no global merge lease
BASE_MAIN_SHA: c1b828734527bae6141805581693d890cc3bff94
BRANCH: agent/s-20261103-210f5f9e/optimization-001
CLAIM_REF: claims/v7/main-protection-preflight (atomic claim branch; not a merge lock)
OWNED_FILES: tavern_ai/v7_merge_entry_audit_210f5f9e.py; tests/test_v7_merge_entry_audit_210f5f9e.py; .github/workflows/v7-merge-audit-210f5f9e.yml; own records
SOURCE: fully read V7 Gmail attachment (32,014 bytes); Issue #182 race evidence
LIVE_MAIN_OBSERVED: protected=false; protection.enabled=false; status check enforcement=off; GET rulesets=[]
PREVIOUS_MERGES: #164, #165 merged by OTHER sessions, not us
CURRENT_MAIN_CI: https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964 was in progress at first check; check exact final SHA
OWN_MERGED_PRS: 0
MODEL: registered 1408-step unpromoted V5 Release https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617
MODEL_SHA256: a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632
ENGINE: TavernGym 1.1.0; observe2 4017/447/245
OPTIMIZER_RESUME_OWN: not run; historical source model release resume recorded, not re-verified here
NEW_PPO_STEPS: 0
NEW_MODEL_RELEASE: none
NEW_GAMES: pending own baseline engine workflow seed 99817, no receipt claim until verified
HISTORIC_MODEL_HELDOUT: [8,8,8] vs baseline [6,8,8] n=3; no improvement
CHAMPION/BEST: null
OWN_PR: pending
KNOWN_BLOCKER: main is not protected and CAS coordination ref is not enforced across all merge writers. No exclusive merge permission.
NEXT_ACTION: check own unique workflow original run, import real receipt if complete, verify PR latest head CI; require protected Merge Queue or one designated integrator before merging.


## Completed original Actions and source verification (update)
- Own exact commit e5b066f3089b47067655a26827f6b6a0ed334f2e triggered Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41513485387 .
- Workflow completed SUCCESS; same-run job ran synthetic negative unit regressions, fetched live GitHub branch protection/rulesets, installed pinned TavernGym 1.1.0, verified engine contract and completed genuine eight-seat baseline seed 99817.
- Original Artifact ID 13173788183, ZIP SHA256 682553b6b17e07f2055501ee69d5cc9e431bbd4924cfac82418d13f28789882b. Original full-game receipt SHA256 321665f1b50c8c0111d4d6a12a6a016a2cd570692db47457aeb739d2ae8fc871, committed unchanged in experiments/s-20261103-210f5f9e/001-99817.json.
- Actual game: seed 99817, seat 0 rank **7**, placements [7,5,2,4,1,8,3,6], 14 turns, 64 decisions, completed, truncated combats=0, turn_limit_end=false, policy=baseline, model_sha256=null. NOT an inference or PPO training result.
- Original live negative-gate report sha256 bd6ef95b8c1dcc89b5f77808cb2d4d8264c18d8715c2720481a11575ffc35471 (committed at reports/s-20261103-210f5f9e/001-main-merge-entry-audit.json); false exclusivity from unprotected main is supported.
- Main #165 exact-HEAD CI https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964 completed SUCCESS, with actual independent baseline game job success; merged by another session.
- PR gate remains separate: create own non-Draft PR, verify its exact current-head unit/game CI and external reviewer; no global main-merge lock, no own merge, no new PPO steps, no own candidate Release.
