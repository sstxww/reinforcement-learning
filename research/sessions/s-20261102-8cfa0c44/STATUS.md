# Session s-20261102-8cfa0c44 — STATUS (through Round 002)

## Session branches, PRs and verification state

- Session ID: s-20261102-8cfa0c44.
- Original main SHA: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
- R001: agent/s-20261102-8cfa0c44/optimization-001, draft PR https://github.com/sstxww/reinforcement-learning/pull/49.
- R001 final-head PR CI: **success** https://github.com/sstxww/reinforcement-learning/actions/runs/41417333511 (commit 3dcc424dbc9481f786a2a2abb6569d60f4430254).
- R002 active branch: agent/s-20261102-8cfa0c44/optimization-002, stacked from own R001 3dcc424d. Draft PR https://github.com/sstxww/reinforcement-learning/pull/56; targets main with dependency on PR #49. Latest-head PR CI must be checked before integration.
- State: two completed real-engine experiments, both **negative for throughput improvement**, pending R002 latest-head CI and human review. Do not merge as a positive performance improvement.

## Real experimental work

- R001 run https://github.com/sstxww/reinforcement-learning/actions/runs/41416657474: 21 tests passed, 13 complete games. Seed 28700 rank 8, 49 decisions, 13 turns, no engine guards; six same-seed pairs match. Serial 0.042792s vs newly spawned two-process 0.324538s. Fresh processes were slower.
- R002 run https://github.com/sstxww/reinforcement-learning/actions/runs/41417665959: 26 tests passed, **385 complete games** (1 own + 128 serial + 128 fresh + 128 persistent). Seed 28800 rank 7, 57 decisions, 16 turns, placements [7,8,4,1,6,5,2,3], no truncation or turn-limit end. All 128 seed triplets match.
- R002 128-game total time: serial 0.528338156s; fresh pools 1.781220916s; persistent pool 0.663245283s. Persistent reuse beats repeated spawn but remains 25.5% slower than serial.
- Environment: exact TavernGym 1.1.0, source hash 6d8712c93022ba11, 4017 floats, 447 cards, 245 legal-masked actions.
- Actual training: **0 PPO gradient steps** in either round; this is evaluation infrastructure, seat 0 unmodified V0 rule baseline. **No new model/checkpoint, training parameters, model SHA256, Candidate/Latest/Best promotion or strength improvement.**

## Evidence and recovery

- First-round receipts: experiments/s-20261102-8cfa0c44/001-*.json; summary reports/s-20261102-8cfa0c44/throughput-001.json.
- Second-round real receipts: experiments/s-20261102-8cfa0c44/002-*.json (independent and representative); complete compact per-seed comparison reports/s-20261102-8cfa0c44/persistent-002.json.
- Studies: research/sessions/s-20261102-8cfa0c44/round-001.md and round-002.md. Proposals: research/knowledge/proposals/s-20261102-8cfa0c44-001.md and -002.md.
- R001 Actions Artifact 13127303717 expires 2026-12-02T08:58:16Z.
- R002 Actions Artifact 13127299935 expires 2026-12-02T09:06:03Z.
- Compact JSON evidence has been committed on respective own branches. No model weights or optimiser checkpoint were produced, so model recovery is not applicable.
- Failure audit: no software error was encountered in successful dedicated experiments; unproven/improved performance was NOT asserted.

## Next research handoff

Do not default to multiprocessing for tiny baseline matches. The remaining meaningful but untested hypothesis is that slow MaskablePPO inference might change the crossover threshold; any future model experiment must isolate model hashes and train budgets, pass fully model-controlled real games and compare independent held-out seeds. Do not extrapolate the above native V0 timings. No Arena ranked participation was performed.
