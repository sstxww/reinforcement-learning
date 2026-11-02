# V7 atomic task claim
SESSION_ID: s-20261103-ab083974
TASK_KEY: review/pr-175-rollback-race
ROUND_ID: 001
ROLE: REVIEWER
BASE_MAIN_SHA: 3a745c6f6a48c65528bcbeb81b8627b8db93f046
CLAIM_BRANCH: claims/v7/review-pr175-rollback-race
TASK: Independently reproduce and review PR #175 rollback ownership race; do not edit PR #175 branch or shared release_restore_entry.py.
OWN_WRITES: research/sessions/s-20261103-ab083974/, research/knowledge/proposals/s-20261103-ab083974-001.md, reports/s-20261103-ab083974/, unique workflow (if evidence run warranted).
CLAIM_KIND: unique deterministic GitHub branch creation succeeded; task exclusivity only for this exact claim ref, not global merge privilege.
MERGE_PRIVILEGE: NONE; no integration lease acquired.
STATUS: in_progress, to be marked completed with handoff at end; stale claim is not authorization for merging.

FINAL TASK HANDOFF (V7 R001):
- Claim owner finished independent review; no active exclusive merge lease is held.
- Non-Draft PR: https://github.com/sstxww/reinforcement-learning/pull/188
- PR head: 1636b98f6a0c3842788780074702c0fd8751c0b9 (recheck before integration).
- Real own source Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41512257198 COMPLETED SUCCESS (2 unit passes/1 conditional skip and real baseline 8-seat seed 99641 rank 8). Receipt: experiments/s-20261103-ab083974/001-99641.json on own branch; genuine Artifact 13174056126.
- PR latest-head CI https://github.com/sstxww/reinforcement-learning/actions/runs/41512857655 IN_PROGRESS at this handoff write; recheck final before any integration.
- Source PR #175 still blocked by check-then-unlink ownership race, independent evidence: https://github.com/sstxww/reinforcement-learning/pull/175#issuecomment-6586652843.
- Permission boundary: no main merge/force/other branch edits. This claim has no reusable active lock; task status completed, no renewal. Anyone adopting task must check current head and claim status.
- Own training 0, new Release 0, raw PPO games 0, no model promotions.

FINAL EXACT-HEAD CI VERIFICATION:
- PR #188 latest head 1636b98f6a0c3842788780074702c0fd8751c0b9.
- PR CI run https://github.com/sstxww/reinforcement-learning/actions/runs/41512857655 COMPLETED SUCCESS at that exact SHA, including real complete eight-seat baseline CI gate.
- GitHub PR API observed draft=false, mergeable_state=clean, base main c1b828734527bae6141805581693d890cc3bff94.
- Still NOT merged: no proven exclusive integration lease and no independent approval; main head and required gates must be rechecked by actual integrator.
