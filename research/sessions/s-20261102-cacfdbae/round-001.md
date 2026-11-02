# V5 R001 — checkpoint and integration audit

- Session: `s-20261102-cacfdbae`
- Branch: `agent/s-20261102-cacfdbae/optimization-001`
- Starting main: `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`
- Target: `sstxww/reinforcement-learning`; upstream is read-only.
- Distinct focus: unowned model-release inventory and fail-closed checkpoint verification; no changes to shared train/evaluate/CI entrypoints.
- Initial PR snapshot: 68 open (66 Draft); during review PR #43 merged concurrently. Re-query before integration.
- PR #15 is open but depends on Draft PR #9; neither should be merged until its own latest-head CI and all prerequisites are verified. #25 is another engineering-integrity candidate; review independently.
- Latest observed engine contract: TavernGym 1.1.0, `source_hash=6d8712c93022ba11`, observe2 4017/447/245.
- Release API listed six `model.zip` assets with SHA256 digests. These are inventory records, **not yet downloaded or independently loaded** by this session. The registry deliberately has no Champion, Challenger or Latest role.
- Source evidence of weak models: PR #15 reports 1280 steps, four paired held-out games with old/new both 8th each time; scripted baseline 7,6,8,8. This is a PR-reported observation rather than fresh independent replay.
- Separate ongoing #60 experiment reports extremely low purchase frequency for a low-LR model, not yet a proven universal root cause.
- Changes: `tavern_ai/model_registry.py`, `models/registry.json`, `tests/test_model_registry.py`, session-specific workflow and handoff.
- Success gate: release re-download + SHA256 + optimizer + engine metadata + CPU load + genuine 128-step continuation and full eight-seat game. Until GitHub runs validate these, state is **pending**.
- Model promotion: explicitly prohibited; current evidence has not established any competitive gain.
- Next: inspect workflow logs and receipt; if real verification succeeds, update handoff. Then add proper action/available-mask telemetry for the eighth-place diagnosis.

## Actual independent V2 Release and continuation evidence (verified)

- First workflow [41427542987](https://github.com/sstxww/reinforcement-learning/actions/runs/41427542987) failed after V2 Release download at metadata schema check. Historical V2 trainer writes schema 2; the original checker incorrectly accepted only schema 1. No model games/training were performed in that failed run.
- Fix commit [94723a1](https://github.com/sstxww/reinforcement-learning/commit/94723a15e3ba9a8f5f36d721668e21d1487629aa) supports schemas 1 and 2, validates nested V2 engine and checkpoint SHA, adds test. Avoided overlapping [Draft PR #8](https://github.com/sstxww/reinforcement-learning/pull/8) by moving independent inventory to `models/release_inventory_v5.json`.
- Second workflow [41428441545](https://github.com/sstxww/reinforcement-learning/actions/runs/41428441545) **completed success**. Independently downloaded immutable V2 Release, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`; ZIP/optimizer, schema-2 metadata/engine and actual CPU policy load passed.
- Genuine pure V2 model full game: [receipt 001-23002](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-cacfdbae/optimization-001/experiments/s-20261102-cacfdbae/001-23002.json); seed 23002; rank **8**; 134 decisions; 17 turns; fully completed, no simulator guard.
- Genuine MaskablePPO continuation: **128** additional steps from **1280** to **1408**, seed 61102; [training JSON](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-cacfdbae/optimization-001/reports/s-20261102-cacfdbae/resume-training.json).
- New checkpoint SHA256: `f0d9c459b9a96e45c206f2a00196d3d7d3c887bb6fb907918c17c8e3010a2b39`.
- New resumed model-controlled full game: [receipt 002-23002](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-cacfdbae/optimization-001/experiments/s-20261102-cacfdbae/002-23002-resumed.json); rank **8**, 134 decisions, 17 turns, completed without truncation/guard.
- Independent paired baseline comparison on seeds **24000 and 24001**: resumed model [8,8], mean 8.0, top4 0/2, win 0/2; official rule baseline [7,6], mean 6.5, top4 0/2, win 0/2. Model-minus-baseline mean rank **+1.5 worse**. n=2 descriptive ONLY, no strength improvement.
- Durable *unpromoted smoke* Release [v5-s-20261102-cacfdbae-smoke-128](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-cacfdbae-smoke-128) published; actual asset names are `resumed.zip` and `resumed.metadata.json`, plus GitHub-digested SHA. Newly uploaded asset has not been independently re-downloaded, so restoration from this new Release has not yet been verified. It is NOT Champion.
- True receipts and metrics committed by Actions to own branch in `04c6f76004d6d79433d2dbd864db6924ecc921f6`. Final latest-head pull-request CI is a separate gate.
- Root-cause status: rank-eight behavior still occurs after 128 more steps. Short budget is not evidence of learning-rate causality. [Issue #78](https://github.com/sstxww/reinforcement-learning/issues/78) requires legal BUY opportunity and no-progress action telemetry.
