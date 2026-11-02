# s-20261102-aaee3a59 / R001 — fail-closed mainline checkpoint lineage

## P0 verified inventory
- Authorized repo: `sstxww/reinforcement-learning`; original start snapshot main `db5e23ae8c218808821327d806b05d2604cfadfb`, full-game push CI [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040) succeeded.
- Isolated branch created from main `1afd8297e3c661bee3117ac5301b1ca08d64869b` after observing simultaneous merges. Open PR search returned 75 at original snapshot; do not reuse as a live count.
- Reviewed #93: its two-asset Release catalog and tests were based on four candidates, while current canonical registry has **five** candidates. Current main also already includes `release_asset_verifier.py`; duplicate checker/test assertion cannot be merged blindly. Its own exact-head CI success is not proof of forward compatibility. Left unmerged/Draft.
- Reviewed #75 (pinned economy + 3,983-card catalog): evidence and exact-head CI exist, but there are overlapping open card-mechanism PRs #67/#68 and main already contains mechanism audit. It remains Draft pending explicit deduplication and review; no forced merge.
- Reviewed #8 (legacy V1 infrastructure): draft and merge conflict, canonical registry already selectively integrated. Do not merge blindly.
- No existing PR was merged by this session; no main writes, other-agent branch rewrites, or Arena use.

## P1 confirmed defect and isolated fix
Main `.github/workflows/train.yml` previously swallowed failed Artifact download and silently initialized random PPO. Main `train.py` produced schema-1 metadata without external checkpoint SHA256 or parent checksum; this permitted accidental loss of lineage. Main evaluation recycled seed 24000 on every run.

This branch proposes:
1. Verify previous successful-run Artifact with recorded archive SHA256 and full ZIP/engine preflight; if missing/unverifiable, use **registered immutable Release** with both Release asset SHA256 checks and engine/optimizer ZIP preflight.
2. Require actual one-step model inference before training. If both sources unavailable/corrupt, fail; only manual `fresh_start=true` may intentionally train from random initialization.
3. Save fresh checkpoint SHA256 and parent SHA256 in training metadata; consume input from a different directory so a failed training run never overwrites source archive.
4. Rotate heldout seed range by GitHub run ID instead of recycling 24000.
5. Add strict synthetic tests for corrupted ZIP, tampered metadata, absent checksum, unknown latest release and missing files.
6. Add session-only bounded workflow to do a real pinned-engine baseline game, authentic latest-Release preflight, **128** PPO continuation steps, candidate checksum/inference preflight, and candidate-controlled no-rescue eight-seat match. A run is an execution attempt until Actions logs and receipts confirm actual completion.

**Existing durable checkpoint (registry claim, corroborated by prior source runs):** latest unpromoted Release `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, 1408 steps, 3 heldout model ranks [8,8,8] against baseline [6,8,8]. No Champion. Do not confuse registry assertion with a fresh independent download here.

## P2 eighth-place evidence and limits
Main and open PR evidence independently show V2 action-mask-legal BUY opportunities neglected in real game; new #107 negative ablation showed that forcing 46 purchases across three games still left all three rank eighth, with Play/Cancel cycles. This weakens a 'buy more alone' explanation. Need prospective action-family progression diagnostics and model-only unguarded game before claiming a causal root.

## Live execution gate
- No model training steps or newly completed match are claimed by this document before the session-specific Actions run finishes.
- Branch-only workflow: `.github/workflows/v5-resume-s-20261102-aaee3a59.yml`; baseline seed 94431, continuation seed 94432, model-only match seed 94433.
- Its short-lived Artifact is **not** durable storage. Never promote/overwrite Champion or `models/registry.json` based on this smoke.
- PR must remain Draft until latest-head CI, authentic receipts, recovery tests, source compatibility and integration review pass.
- If smoke fails, inspect exact job log, commit failure report in own session, and fix at most two reasoned attempts.

## Next integrator actions
Check newest main SHA, latest PR head and job logs; compare changed shared `train.py`/`train.yml` against concurrent integrations; preserve model source; run a bounded mainline restore regression; after passing canary + PR CI consider merging. Then test fresh independent paired seeds and seat rotations before any larger training.
