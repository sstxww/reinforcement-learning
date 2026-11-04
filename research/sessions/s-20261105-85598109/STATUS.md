# s-20261105-85598109 V7 review/pr187-evidence — R001
Status: running (read-only review completed; own real eight-seat baseline pending).
Role: REVIEWER. TASK_KEY: review/pr187-evidence. Atomic task claim ref: claims/v7/review-pr187-evidence (task claim only, NOT integrator exclusive merge authority).
BASE_MAIN_SHA: c1b828734527bae6141805581693d890cc3bff94
Latest verified main SHA: c1b828734527bae6141805581693d890cc3bff94 (GitHub /branches/main API).
Own branch: agent/s-20261105-85598109/optimization-001; this handoff will be updated after Actions.
PR under review: #187; expected HEAD cb7249e47399f90a55fca5038ce4de4302490ba0; non-Draft, mergeable at inspection. PR independent review submitted: 5774195418.
Actual merge result: NONE; no sole integrator gateway and main protected=false, repo rulesets=[]; Issue #182 documents CAS-bypass.
Main postmerge CI: N/A. Exact current-main successful CI: https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964.
PR #187 exact-head successful CI: https://github.com/sstxww/reinforcement-learning/actions/runs/41515486403; 395 passed/1 skipped, genuine eight-seat baseline seed1001 rank7, no truncations. This game belongs to PR #187's CI, NOT this session.
Historical actual PPO resume: https://github.com/sstxww/reinforcement-learning/actions/runs/41512678144; 1408→1536, +128 PPO steps done by original PR #187 author; own training steps 0.
Paired original run https://github.com/sstxww/reinforcement-learning/actions/runs/41513659254: raw model rank8 vs baseline ranks2/6 at seeds 97832,97833, same seat and seed, n=2, negative. No guard/fallback model improvement claimed.
Registered parent: v5-s-20261102-68099929-1408-41428692617 (SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632); TavernGym 1.1.0 observe2 4017 floats/447 cards/245 actions engine source hash 6d8712c93022ba11.
Rejected child Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v7-rejected-s-20261103-581c69c0-r001-d6771d4439d1 ; model SHA256 d6771d4439d1deb64231edd4caaf9ebbc8cd2f8db667c94b19a8c144b968b096; ZIP 17,525,202 bytes and optimizer verified in original 41513659254; NOT Latest/Best/Champion. Current main best=null, champion=null.
Own eight-seat game: NOT YET executed at this status snapshot; planned own bounded isolated baseline only. This is infrastructure evidence, not candidate model evidence.
Owned file set: research/sessions/s-20261105-85598109/, research/knowledge/proposals/s-20261105-85598109-001.md, reports/s-20261105-85598109/ and own one-shot workflow only. No production trainer/registry modifications.
Verified defect in #187 being addressed: schema-2 incompatible parent rejection should happen before MaskablePPO.load/learn; patch and synthetic tests checked.
Remaining systemic blocker: globally enforced single merge entry/branch protection absent. Task claim != main merge lease.
Exact next action: inspect own Actions game run for completion and original receipt, commit evidence, rerun latest HEAD CI after final branch commit, hand #187 to independently authorized integrator. Never merge solely with this claim.
