# s-20261102-75cf9e03 — R001/R002 execution addendum

R001's isolated GitHub Actions run 41427453982 **succeeded**. The first PR CI on SHA `56e0452` ran **87 passing tests** but failed the independent receipt gate only because the dedicated canary was still running. The dedicated run installed pinned TavernGym and completed a genuine eight-seat baseline game, committed receipt in the same session branch: seed 65810, rank 8, decisions 33, turns 16, placements [8,7,1,6,5,4,2,3], all required guards clean. This is not model evaluation or PPO training.

**P2 evidence reviewed:** PR #60 (dependent on PR #51) provides six genuine model-controlled heldout matches: 1e-4 model [8,8,8], 21 model END_TURN and 0 BUY over 36 actions; 3e-4 model [8,8,7], 20 BUY, 788 other actions, 21 forced END_TURN and longest repeated streak 40 (3 seeds per arm). Neither causal low-LR blame nor an action-mask bug has been established. This is an actionable hypothesis, not a verified model fix.

**P1 R002 launch:** New branch-specific bounded workflow independently downloads the published **unpromoted V2** release `v2-learning-41413557445` (expected SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`), runs strict preflight and a one-step real model inference, then attempts a 128-step genuine continuation from total 1280 to 1408. It requires actual eight-seat model game seed 65811 and successful upload to a unique **unpromoted** GitHub prerelease before committing a success receipt. Failures must be read from logs; a 30-day Artifact alone is not a permanent model. No model is promoted. R002 pending actual runtime verification; no results asserted here.

All changes remain in our isolated PR branch; no direct main push, no ranked Arena or upstream write. 
