# Session s-20261102-99372431 — current verified state (round 002)

**Role:** independent V5 P0/P1 integration and limited P2 evidence. Only writes own isolated branch; no main push or Arena.

**Draft integration PR:** https://github.com/sstxww/reinforcement-learning/pull/127
**Branch:** `agent/s-20261102-99372431/optimization-001` (original base main `1afd8297e3c661bee3117ac5301b1ca08d64869b`)
**Executed workflow:** https://github.com/sstxww/reinforcement-learning/actions/runs/41449843877
**Raw temporary evidence Artifact:** https://github.com/sstxww/reinforcement-learning/actions/runs/41449843877/artifacts/13143847982
**Durable unpromoted checkpoint:** https://github.com/sstxww/reinforcement-learning/releases/tag/v5-resume-s-20261102-99372431-41449843877
**New checkpoint SHA256:** `0f2c9705fb1078815f3c74d511aa3a770550b2348d1528072920f1bec02539f8`

## Verified execution

- Source persisted 1,408-step experimental checkpoint, external SHA256 and pinned engine preflight succeeded, actual CPU masked model inference succeeded.
- **128 real MaskablePPO PPO training steps** added for cumulative **1,536**. Schema-2 metadata with full compatibility and lineage persisted and preflighted; real masked inference from new weights succeeded. The new Release asset digest matches local computed SHA, but *independent redownload of new Release* was not done by this original run (added as a future run gate).
- Real independent full eight-seat baseline game, seed `99372431`, rank **7**, 18 turns, 47 decisions, true complete.
- Real **raw** model-controlled full eight-seat game seed `99372432`, rank **8**, 17 turns, 120 decisions, true complete, no combat truncation or end-turn-limit stop.
- **No paired same-seed comparison or proven model improvement. No Champion/Best promotion.**
- The overall isolated workflow reported failure at the *evidence push* after all training/game/Release steps succeeded. Log conclusively shows non-fast-forward when session documentation commits advanced remote. Original four machine-generated JSON artifacts have since been recovered verbatim from raw Action logs and committed into the branch. Full failure report: `research/sessions/s-20261102-99372431/failures/001-evidence-nonfastforward.md`.
- Workflow maintenance fix was committed: opt-in push trigger, rebase before evidence push, new Release readback; **not rerun yet**.
- First PR CI failed solely because it ran before own receipt existed (244 unit tests passed); the later CI for the latest SHA must be checked.

## Integration and research gates

- No PR has been merged by this session. #15 is ready but stacked on Draft #9, so cannot safely merge directly into main; deduplicate current main with existing checkpoint work first.
- Prior #103 guarded V2 had 521 legal BUY opportunities with 0 purchases; #107 forcing 46 buys on 3 seeds remained rank 8 and played many Play/Cancel loops. These are small noncausal studies, not proof of a single reward or model error.
- Next: await **actual latest-head** PR CI, verify new model Release redownload on an explicit further check, run paired 1408 vs 1536 evaluation on independent seeds and diagnose Play/Cancel state-progress loops; only integrate after review and current-main compatibility. No blind further training.
