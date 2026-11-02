# s-20261102-75cf9e03 — V5 verified integration status (R004)

## Direct integration
- **P0 PR #90 merged to main by this session:** https://github.com/sstxww/reinforcement-learning/pull/90 ; merge commit `fd5ffefe2a2067cd581edfdf620976ebb6ba684a`. Main CI on that exact merge SHA **passed**: https://github.com/sstxww/reinforcement-learning/actions/runs/41429890388.
- PR #90 authentic paired V2 PPO vs baseline seeds 45111/45112: PPO [8,8], 74 legal BUY decision exposures, 0 BUY, 222/248 Refresh/Freeze actions; baseline [6,7], 33 BUY/48 exposures. This supports action-selection failure, not causal reward proof or improved strength.
- Our independent preflight/archival PR: https://github.com/sstxww/reinforcement-learning/pull/79. All files isolated from shared trainer, main workflow, registry and other sessions.

## Actual separate execution
- R001 [success](https://github.com/sstxww/reinforcement-learning/actions/runs/41427453982): original synthetic integrity tests + genuine full eight-seat **baseline** seed 65810 rank 8, 33 decisions / 16 turns; receipt in `experiments/s-20261102-75cf9e03/001-65810.json`.
- R002 [training succeeded, strict model game failed](https://github.com/sstxww/reinforcement-learning/actions/runs/41428024110): read durable V2 Release, real 128 PPO steps from 1280 to 1408, final model SHA256 `7eac498b502a233f7ca04b351200429f2ea8142dbec47c421f7b8f3544646a8b`. Unguarded model-only seed 65811 failed `Full-game safety limit exceeded`. Do not invent rank.
- R003 [real preflight succeeded, guard-assisted analysis failed](https://github.com/sstxww/reinforcement-learning/actions/runs/41429113481): independently recovered exactly hashed output, ZIP optimizer component integrity, `MaskablePPO.load`, one legal masked inference PASS. Alternative guard timed out at mask-illegal END_TURN; no completed guarded or unguarded game. Abandoned duplicate tracer in favor of merged PR #90.
- R004 [archive succeeded](https://github.com/sstxww/reinforcement-learning/actions/runs/41430345890): durable https://github.com/sstxww/reinforcement-learning/releases/tag/v5-rejected-s-20261102-75cf9e03-41430345890 with actual `model.zip` (17,525,156 bytes), `model.metadata.json` and `004-rejected-archive.json`. Official asset SHA256 matches the resumed model. Prerelease explicitly **Rejected/diagnostic-only**, not Best, not a Champion, no strength claim.
- R002 preflight issue: source Release metadata schema 2 vs old preflight schema 1; and `| tee` masked failure. Fixed schema 1+2 compatibility and fail-closed pipe in isolated code. Current main train after loading V2 schema2 wrote schema1, dropping catalog/patch compatibility; reported as blocker to Draft PR #9.

## Integrity/promotion
- Training steps this session: **128** total; new checkpoint cumulative **1,408**. No further training until underlying action pathology is corrected. No Arena, no upstream writes.
- Main registered Champion: unchanged; experimental V2 and our rejected resumed output must not be auto-promoted.
- Old costly train and baseline workflows switched to manual dispatch. Dedicated archive source workflow runs on its own isolated path only. Any merge of PR #79 requires final exact-head CI and integration review.
