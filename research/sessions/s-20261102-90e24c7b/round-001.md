# V5 R001 — Integration and opportunity-aware V2 diagnosis

Session: s-20261102-90e24c7b
Base main SHA: 31dc7c82ad2fcba461706b4f324d743b5c1c2b9e
Branch: agent/s-20261102-90e24c7b/optimization-001

## P0: Actual integration completed

Reviewed and squash-merged GitHub PR #69 (hidden-state noninterference regression) after exact-head passing full-match CI, clean merge check and complete eight-seat receipt.
Merge commit: 31dc7c82ad2fcba461706b4f324d743b5c1c2b9e.
Post-merge CI: https://github.com/sstxww/reinforcement-learning/actions/runs/41427702749 — status must be verified; this report does **not** claim success until GitHub confirms it.
This merge adds tests and no stronger model.

P0 audit findings at branch creation: 63 open PRs, 62 Draft and one non-Draft (#15), which depends on Draft #9. Infrastructure #8 is conflicting, unverified on latest head. Main has no production registry, and train.yml retrieves only expiring Artifacts, not durable Releases.

## P1: Checkpoint baseline and blockers

Durable GitHub Release v2-learning-41413557445 contains an unpromoted 1,280-step model.zip; reported SHA256:
73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a
Source run https://github.com/sstxww/reinforcement-learning/actions/runs/41413557445.
Previous four heldout placements [8,8,8,8] vs rules baseline [7,6,8,8]. No Champion.
A registry exists only in unmerged infrastructure PR #8. Other active sessions are investigating model registry and restoration, so this branch does not modify shared train.yml, existing trainer, registry or model weights. Release independent hash/load verification is attempted in our isolated Actions run, and the result must be observed before making any new recovery claim.

## P2: Why place 8?

Prior real telemetry in dependent Draft PR #60 (following #51), seeds 42174–42176:
low-LR candidate placements [8,8,8], 36 model decisions, 21 end turns, zero Buy, zero forced guard;
reference [8,8,7], 875 decisions including 20 Buys, 21 forced guard ends and 40-action identical-action streak.
This demonstrates a behavioral abnormality for those models/seeds but **not** whether buying was legal, nor a causal effect of learning rate.
Our new, independent probe targets the durable V2 1,280-step Release, not those PR #60 weights. It counts action-mask legal-buy opportunities and chosen buys, forced safety ends, and posthoc **own-seat** economic/board state, without leaking hidden data into the policy.

## Executable experiment

New session-scoped module: tavern_ai/v2_opportunity_s_90e24c7b.py.
Pinned TavernGym 1.1.0, engine source hash 6d8712c93022ba11, observe2 features 4017 / cards 447 / actions 245.
Exact Release model SHA256 and 1,280 saved steps are asserted before inference.
Three fresh fixed heldout seeds: 89101, 89102, 89103.
For each seed: one unchanged BaselinePolicy seat0 full game and one model-controlled seat0 full game (total planned 6). Guard action cap at 75 per own turn, if legal, is transparently counted; it may prevent identifying raw full-game completion. Each game must reach Game.is_over() and pass strict receipt integrity.
Report paths: reports/s-20261102-90e24c7b/001-opportunities.json; experiments/s-20261102-90e24c7b/001-{baseline,model}-{seed}.json.

**Execution state: workflow not yet verified when this document was authored.**
Do not claim those six games or V2 recovery happened until the workflow succeeds and creates validated receipts. No new PPO steps planned in this round; if purchase behavior is abnormal, recommend specific next corrective experiment before extending training.

## Controls and limitations

- Only public own-seat observe2 arrays + current legal-action mask are provided to model.predict.
- Game.view(0)["me"] is an **offline diagnostics-only** observation; it is never used by policy.
- Number of steps with Buy legal is not count of independent, affordable opportunities.
- Safety guard is always disclosed; guarded model results are not the pure raw model result.
- This is diagnostic, not a power claim. Never enter ranked TavernArena without separate permission.
- Branch-only workflow commits only own experiments and reports. No modification of other sessions, main, upstream or shared training jobs.
