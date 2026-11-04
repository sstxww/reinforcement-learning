# R001 — Independent review of existing PR #187, avoid duplicate trainer PR

## Scope & inherited evidence
Before creating another trainer fix, audited #187 and existing main, including code patch and its real CI. Current main c1b828734527bae6141805581693d890cc3bff94, latest main CI 41512315964 succeeded. Repo branch API protected=false and /rulesets returned []; branch protection GET yielded integration-token 403, so no enforced path was established. Issue #182 documents prior CAS loophole.

## Actual review
Submitted COMMENT review 5774195418 on exact HEAD cb7249e47399f90a55fca5038ce4de4302490ba0. Current metadata says PR is non-Draft/mergeable (not a merge authorization). Verified patch calls preflight before MaskablePPO.load, schema-2 compatibility checks, 114-line synthetic test; latest-head CI 41515486403 completed success, 395 passed/1 skipped, five committed game receipts validated and one genuine eight-seat baseline match finished (seed 1001, rank 7, no truncations).

Source training run 41512678144 demonstrates real 128 MaskablePPO continuation steps (1408 to 1536). Independent paired run 41513659254 verified candidate, produced model rank8 vs baseline2/6 on same seeds 97832/97833, and published immutable rejected Release v7-rejected-s-20261103-581c69c0-r001-d6771d4439d1 with exact model SHA256 d6771d4439d1deb64231edd4caaf9ebbc8cd2f8db667c94b19a8c144b968b096. These are original PR #187 accomplishments, not own session runs.

## Important negative finding
Green CI and mergeable=true cannot prove global serialization. A CAS ref alone failed in #182; protected=false and no rulesets means do not invoke GitHub merge API. No independent approval can be submitted via the authenticated same-user account. Do not mislabel latest raw model as Champion; n=2 evidence is negative.

## Own isolated follow-up
One-shot bounded baseline Actions on own isolated branch; own PPO steps 0, own model Release not applicable to review scope. Do not invent an own model rank. After actual run, archive original receipt, update status and create ready-for-review handoff PR if the game and PR CI succeed.

## Success/failure distinction and next action
Review completed and recorded on live PR; no main merge, no new training, no own completed match at the initial snapshot. First handoff action: verify own real game output and exact finalized HEAD Actions; then pass #187 to a single demonstrably exclusive integrator.

## Final authenticated own run (not inherited from #187)
Actions #41894485131: completed SUCCESS, job #126800246252; original one-shot workflow head 7afc459d76d04ee1f25d28158bc1f7ed2f7caf74. Genuine pinned TavernGym 1.1.0 eight-seat baseline seed 117459, agent s-20261105-85598109, completed true, 18 turns, 47 decisions, placements [7,1,5,6,3,2,8,4], controlled rank 7, no truncation, no turn-limit ending. Original JSON in experiments/s-20261105-85598109/001-117459-baseline.json, blob 8132962ed26afcba90a3847063da810a79ff72c6. Immutable run artifact #13353459949, expiring 2026-12-04. Own PPO training 0; no new checkpoint, optimizer, Release or model rank; one-shot workflow removed from final PR diff after successful run.

## Distinct code review finding after comparing overlapping PRs
[#187 comment](https://github.com/sstxww/reinforcement-learning/pull/187#issuecomment-6639679985): `schema=True` reaches `parent.get("schema") == 1` in #187's shared metadata helper and is accepted as schema 1; wrong-type signed metadata can bypass schema-2 provenance validation. #196/#202 guard with `type(schema) is int`; #196 also checks `increment_timesteps` bounds. Integrate one reviewed fix with regression, not all three overlapping trainers. This finding comes from exact source comparison, not a claimed local test result.
