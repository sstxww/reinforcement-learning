# V5 R004 — recovery, rejected weights and integration handoff

**Date:** 2026-11-02. **Session:** s-20261102-75cf9e03. No child agents or shared-branch writes.

### Authentic trained model lineage
Durable source `v2-learning-41413557445`: original 1,280 steps, trusted source hash `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. Own R002 run #41428024110 successfully resumed actual CPU `MaskablePPO` for +128 steps, yielded 1,408-step model SHA256 `7eac498b502a233f7ca04b351200429f2ea8142dbec47c421f7b8f3544646a8b`. The raw model-only complete-eight-seat game on seed 65811 failed `Full-game safety limit exceeded` so it has **no valid rank**.

R003 run #41429113481 independently recovered the exact checkpoint from temporary Artifact #13133071390; archive+optimizer integrity, engine fingerprint, loading model and one actual legal masked inference all passed. The separate heuristic guard diagnostic aborted when its attempted END_TURN was mask-illegal, without claiming a completed match.

R004 run #41430345890 independently SHA-verified the real failed checkpoint, validated metadata, successfully published immutable prerelease [v5-rejected-s-20261102-75cf9e03-41430345890](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-rejected-s-20261102-75cf9e03-41430345890). Release contains complete model ZIP, adjacent metadata and `004-rejected-archive.json`; GitHub asset ZIP SHA256 equals source recovered checkpoint. Classification `rejected_diagnostic_only`; Champion and latest promotable model unchanged. This resolves V5 P1 failed-checkpoint loss for this session.

### Real P2 root-cause evidence integrated into main
Integrated own verified PR #90 (merged SHA `fd5ffefe2a2067cd581edfdf620976ebb6ba684a`, postmerge main CI #41429890388 success). V2 PPO on two matched seeds chose zero BUY despite 74 BUY-legal decision exposures; 222/248 actions were IDs 1/2 (Refresh/Freeze in pinned upstream), rank [8,8]. Baseline purchased 33 times across 48 exposures, rank [6,7]. Strong direct evidence of action utilization malfunction, **not** experimental proof of which reward/training term causes it.

### Failure of attempted gate and actual fixes
Original R002 preflight only knew `schema=1`, unlike V2 Release `schema=2`, while shell `tee` masked the exception. Fixed tool accepts both with mandatory schema-2 full compatibility and inner SHA; new sources require `set -euo pipefail`. Separate expensive study workflows made manual-only; new source-only archive workflow persists diagnostic failure outputs without requiring a valid game. Removed unverified duplicate guard tracer from our PR. Delivered schema downgrade concern to stacked Draft PR #9.

### Stage gates
- **Passed:** actual trusted V2 Release recovery, 128 PPO continuation, 1,408 ZIP hash, checkpoint load/probe, permanent rejected model archive, isolated unit and authentic baseline run, PR90 exact-head + postmerge CI.
- **Failed:** raw model-only full game, meaningful competitive ranking, proof of policy improvement. `best = null` remains appropriate.
- **Next allowed work:** intervention against Refresh/Freeze overuse on held-out paired games, state-delta trace, improved structured reward/action masking and safe optimizer/metadata compatibility before increasing training beyond 1,408; coordinate via existing PR #90/#9, not duplicate large experiments.
