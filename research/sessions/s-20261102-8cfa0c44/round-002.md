# Round 002 — Amortizing Python process-pool initialization

## Identity and context

- Session: s-20261102-8cfa0c44, round 002
- Branch: agent/s-20261102-8cfa0c44/optimization-002
- Original main reference: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Stacked from own round-001 head: 3dcc424dbc9481f786a2a2abb6569d60f4430254; dependency PR #49.
- Source commit: 9f81b7982c9b58c492a2ded01bc1263b2b9d4d0e
- Test commit: 87fa769f9e09b26492eefbb53038a152e2d60dc2
- Workflow commit executed: 27a5923453c68ac057c149e598d47c652df46ccf
- Evidence commit: dbb0aed (verified GitHub Actions job log).
- Real successful run: https://github.com/sstxww/reinforcement-learning/actions/runs/41417665959
- Summary: reports/s-20261102-8cfa0c44/persistent-002.json

## Hypothesis

Round 001 found that newly spawned workers made a six-game batch 7.58 times slower than serial. The new hypothesis was that reusing two worker processes across multiple genuine TavernGym batches could amortize spawn overhead and become faster than serial, while retaining identical per-game outcomes.

Round 001, existing PR #26 on seeded replay, and project main docs were rechecked. There was no other open PR claiming this particular persistent-process-pool experiment. No shared code was modified.

## Implementation and bounded experimental design

Only adds tavern_ai/persistent_pool_eval.py, tests/test_persistent_pool_eval.py, and a dedicated own-branch workflow. Inherits round-001 module, tests, real receipts and research records without overwriting them. Three arms:
1. Serial: four batches of 16 consecutive seeds on one process.
2. Fresh: for each batch start and close a two-worker spawn ProcessPoolExecutor.
3. Persistent: start one two-worker spawn pool and reuse it for all four batches.

Trial 1 seeds 28801–28864 used serial, fresh, persistent order. Trial 2 seeds 28901–28964 used reverse persistent, fresh, serial order. Thus each mode executed 128 full real eight-player games, plus a distinct mandatory own match seed 28800: **385 total**. Each replay compares seed, engine, policy, turns, decisions, placements, completion and protective guards before accepting metrics.

Seat 0 always uses unmodified V0 baseline, against seven TavernGym scripted bots. No policy learning occurred and no strength improvement is implied. To prevent huge evidence spam, compact per-seed statistics for all 384 arm matches are in the JSON report; seven individually validated representative/independent raw JSON receipts are in experiments/s-20261102-8cfa0c44/002-*.json.

## Genuine engine, tests and receipt

- TavernGym 1.1.0 source hash 6d8712c93022ba11 (verify_engine checked).
- 4017 float features, 447 card slots, 245 legal-masked discrete actions; 3984 card index vocabulary.
- Pinned upstream commit fb61201a557ddd36a411cf44aac51ce4d9b606ce and observe2 patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
- Policy/runner source SHA256 dadb647e23bf8b06736fc1917e03e1b4f9ae5e4a8304ed17c7ef87af46b615d6.
- The successful job passed **26 tests**, all engine checks, 385 full real games and paired equivalence, then committed actual evidence to the own branch.
- Mandatory genuine receipt experiments/s-20261102-8cfa0c44/002-28800.json: seed 28800; seat-0 rank 7; placements [7,8,4,1,6,5,2,3]; 57 decisions, 16 turns, completed Game.is_over true, truncated combats 0, turn-limit end false, no illegal-action exception.

## Actual benchmark outcome

Each arm ran 128 games. Total timed batches across both trials:
- Serial: 0.528338156 s, approximately 242.27 games/s.
- Fresh two-worker pools: 1.781220916 s, approximately 71.86 games/s.
- Persistent two-worker pools: 0.663245283 s, approximately 193.0 games/s.
- Persistent versus serial throughput ratio: 0.796595. Even persistent workers ran around 25.5% longer than serial.
- Persistent versus fresh time speedup: approximately 2.69 times. Reuse helps relative to repeated spawning, not enough to win against this serial workload.
- Trial 1 (64 games/arm): serial 0.274499s, fresh 0.908908s, persistent 0.326013s.
- Trial 2 (64 games/arm, reversed order): serial 0.253839s, fresh 0.872313s, persistent 0.337233s.
- All 128 seed triplets agreed on all checked gameplay fields, no detected truncation/illegal action.
- Baseline seat-0 mean rank: 7.171875 for every arm (trial means 7.046875 and 7.296875). First-place 1/128 = 0.78125%; top-four 4/128 = 3.125%. These are identical repeated games, NOT three independent samples for policy-quality claims.
- This sample is 2 timing trials on a single runner, not universal proof for heavier neural inference or alternative hardware. Execution order was reversed to reduce one-sided ordering effects but did not eliminate all noise.

Actual PPO steps: 0. PPO configuration: not applicable; V0 original scripted rule strategy only. Model hash/checkpoint: none, so Best, Candidate and Latest model identities unchanged.

## Preservation, failure analysis and conclusion

Full run 41417665959 and artifact 13127299935 preserve verification evidence; 30-day artifact expires 2026-12-02T09:06:03Z. Compact evidence committed to this own branch. No software failure encountered; negative throughput result is not a crash. The workflow is finite, uniquely triggered, with no automated training loop.

**Result: persistent worker reuse substantially mitigates repeated spawn costs but still does not outperform serial for these ultra-short native games.** Recommend continuing serial baseline full-game evaluation under current simulator workload. Consider separate future research for much slower learned-policy inference, batch sizes or native multithreading, with real benchmarks and separate seeded comparisons.

Integration awaits the latest-head PR CI check, review and owner approval; no edits to main, upstream or other sessions.
