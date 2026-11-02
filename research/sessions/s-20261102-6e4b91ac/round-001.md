# V5 R001 — P0 integration triage, P1 verified resume lineage, P2 root-cause evidence

Session: `s-20261102-6e4b91ac`. Branch: `agent/s-20261102-6e4b91ac/optimization-001`. Base main HEAD: `db5e23ae8c218808821327d806b05d2604cfadfb`. Pinned TavernGym 1.1.0, engine source `6d8712c93022ba11`, observe2 (4017 floats/447 cards/245 actions). Scope: only authorized repository, no ranked Arena or upstream writes.

## P0 real inventory and merge gate

The GitHub REST open-PR inventory at 2026-11-02 10:50 UTC contained **75 open PRs, 74 Draft**; sole non-Draft #15 targets an experimental branch rather than main and is dependent on V1 work. No PR was merged in this session: all main-targeting open PRs were Draft and require exact-head review, genuine game evidence, de-duplication and integrator ownership. Notable dependencies: #105 stacks on #90; #107 stacks on #103; #103 author explicitly warns of overlap with already integrated #90/#98. Do not turn Drafts into Ready or merge blindly. Initial main HEAD CI run [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040) succeeded on SHA above. Registry and several checkpoint preflight tools already exist in main; no duplicated registry was created here.

## P1 actual code and tests

`tavern_ai/train.py`: added `validate_resume_metadata` before `MaskablePPO.load`; require compatible schema/engine, positive integer cumulative steps, SHA256 match when recorded, SHA compulsory for schema2; after load compare model internal `num_timesteps` to sidecar; future model saves write SHA256 to metadata. Reused main's `registry_integrity.verify_checkpoint`. Schema1 historical checkpoints without digest remain permitted for compatibility, but their authenticity/integrity is explicitly **unverified**. Self-reported checksum alone does **not** establish trusted Release provenance. Main `train.yml` still uses expiring Actions Artifacts for default resume: durable Release fallback remains a separate P1 integration gap.

12 new offline regression tests passed in [Actions 41449706506](https://github.com/sstxww/reinforcement-learning/actions/runs/41449706506) own-gate job.

**Genuine self-owned complete eight-seat game:** `experiments/s-20261102-6e4b91ac/001-86401.json`, pinned engine; baseline seed 86401, seat0 place 7, turns 15, model-policy decisions 0, baseline decisions 37, all eight placements [7,5,8,6,1,2,4,3], zero truncated combats, no turn-limit end. Validator passed; Actions automatically committed its own genuine receipt at `8d7bcf2`. This is infrastructure evidence only, **not** an RL model improvement.

A bounded isolated workflow also attempts to restore Release `v5-s-20261102-68099929-1408-41428692617` with pinned SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, continue 128 steps and gate on one unguarded model-controlled complete game. Only after all gates may it save a uniquely tagged unpromoted Release; check actual Actions result before claiming training, checkpoint save or full model game success. No Champion promotion.

## P2 evidence from *already merged main*, not a new model result

- `reports/s-20261102-83d91476/001-buy-opportunity-report.json`: real V2 rank [8,8] on seeds 45111–45112; **74 decisions with a mask-legal BUY, 0 selected BUY**, 222/248 raw actions IDs 1 and 2 (Refresh / Freeze); no forced ends. Baseline rank [6,7] with 33 purchases. The denominator counts correlated decision states, not 74 independent opportunities; legal BUY is not always optimal BUY.
- `reports/s-20261102-68099929/003-buy-opportunity.json`: newer 1408-step model on seed 99128: 35 buy-legal decision states, 0 actual buys; both baseline and candidate placed eighth in that single pair.
- `reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json`: guarded V2 ranks [8,8], no purchases on seeds 87102/87103, with guard interventions [4,0]; baseline [5,7]. A guard is not policy learning.

**Confirmed failure signature:** select action family dominates over lawful shopping opportunities, and multiple real model games stay rank eight. **Not established:** whether action selection is caused by bad reward, observation encoding, action mask, optimizer instability or teacher distribution; forced BUY alone has not proven rank improvement. Next bounded causal test should log per-turn public state change and action-family logits, then test a single Play/Cancel or Refresh/Freeze loop intervention on new heldout seeds, separating raw PPO from guarded variants.

## Status and handoff

No policy promotion; no manually fabricated receipt, no large weights committed to Git. Source code changed one shared trainer file; integrator must check concurrent PR diff compatibility. Latest model in main registry is experimental 1408-step Challenger, Champion null. CI and P1 smoke outcomes must be verified at exact final head before merge. If P1 smoke fails, preserve run/job log, do not claim a model save or continue scaling. Main workflows, model register and existing sessions were not modified.
