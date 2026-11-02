# Round 001 — Process isolation versus serial full-game TavernGym evaluation

## Identity and traceability

- Session: s-20261102-8cfa0c44
- Branch: agent/s-20261102-8cfa0c44/optimization-001
- Base main commit: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Source commit: ceb0ca8df075fa739ecc64e3245de4de37b8fad9
- Workflow commit evaluated: f480ed92d69b8efefdcfa1f59a56faa1b7ba2abb
- Results runner commit (as seen in successful job log): c0191dc
- Successful GitHub Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416657474
- Actual seed-by-seed report: reports/s-20261102-8cfa0c44/throughput-001.json

## Hypothesis and research context

Could two isolated Python processes evaluating TavernGym full matches increase throughput without changing action legality or seeded results? Large numbers of simultaneous agents need inexpensive, reproducible held-out games.

Reviewed base project files and all open PR titles. Related but distinct work:
- PR #26 establishes fixed-seed sequential action/observation replay, not process-pool throughput.
- PR #25 audits receipt integrity, not parallel execution time.
- PR #20 guards PPO looping; not reused here.
- PR #12 reports negative reward shaping after real PPO training; we do not claim this experiment improves policy strength.
- PRs #28/#29 demonstrate that some baseline strategy modifications had no observed effect.

## Code and experiment method

Adds only tavern_ai/parallel_eval.py, tests/test_parallel_eval.py, and a unique branch-scoped workflow. Shared baseline.py, canary.py, train.py, train.yml, main, and all other sessions remain untouched.

Uses the actual pinned Game-based canary.run driver. Seat 0 is always the unmodified V0 BaselinePolicy; other seven seats use official TavernGym bots. A standalone seed 28700 is played by the runner. Six held-out seeds 28701–28706 are replayed sequentially and again with a spawn-based ProcessPoolExecutor of two workers. Every game must terminate in the genuine engine, with legal action mask checks; comparison covers seed, engine, placements, turns, decisions, completion and truncation/turn-limit fields. Time measurements cover entire batch, including process startup.

Contract verified by the successful run:
- TavernGym version 1.1.0; engine source hash 6d8712c93022ba11.
- 4017 float observation features; 447 card slots; 245 discrete masked actions; 3984 card indices.
- Upstream pinned commit fb61201a557ddd36a411cf44aac51ce4d9b606ce.
- Verified patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
- Evaluation implementation and policy source SHA256 b2f3b47537a4c3ede3859ac5eed5ec3c35f42a4dbf64511f2451bb8bc09bff75.

## Actual test, training and full-match evidence

Workflow SUCCESS, 21 tests passed, pinned engine installed, thirteen (13) real eight-player games all completed. Unit tests verify workload bounds, duplicate seed rejection and replay divergence detection.

Own mandatory match: experiments/s-20261102-8cfa0c44/001-28700.json.
- Seed 28700; full game ended; seat-0 rank 8.
- Eight-seat placements: [8,5,7,6,1,4,3,2].
- 49 controlled actions, 13 turns, 0 truncated combats; no turn-limit end.
- Model hash: null (rule baseline only).

Paired six-seed results:
- Serial ranks: [8,6,7,8,8,8]; 6 games; mean rank 7.5; first 0/6; top-four 0/6.
- Process ranks: [8,6,7,8,8,8]; 6 games; mean rank 7.5; first 0/6; top-four 0/6.
- All six pairs exactly agree on required gameplay and engine fields. Only process PIDs, timestamp and similar runtime metadata differ.
- Serial full-batch time 0.042792009 seconds, 140.2131 games/sec; one PID.
- Two-process full-batch time 0.324538407 seconds, 18.4878 games/sec; two separate PIDs.
- Serial/process time ratio 0.131855, so the process pool was approximately 7.58 times slower in this short benchmark. No throughput improvement.
- These measurements are one order-fixed batch with process-startup overhead and do not establish general speed ratios for larger simulations or model inference.
- No illegal-action error or simulation truncation was observed; successful receipt validation proves engine completion, not competitive skill.

PPO training steps: **0**, because the tested change is evaluation infrastructure, not a PPO candidate. There is no model checkpoint, optimizer state, or Best/Latest/Candidate model to store or promote.

## Evidence and durability

Real per-game receipts: experiments/s-20261102-8cfa0c44/001-*.json, including the independent game and both replay arms. Summary: reports/s-20261102-8cfa0c44/throughput-001.json. Actions artifact 13127303717 expires 2026-12-02T08:58:16Z (30-day retention); compact receipts are preserved in this session Git branch. Artifact is not an indefinite model backup.

No software failure required a repair. The research hypothesis was disproved under the tested configuration, but tests, game execution and evidence persistence succeeded.

## Decision and next hypothesis

**Do not merge process-per-batch evaluation as a claimed throughput improvement.** This is a useful negative result. For tiny native TavernGym games, Python spawn/startup costs dominate. Keep the baseline serial evaluator until a separately verified regime (large batches, persistent worker reuse, expensive PPO inference) demonstrates a benefit. If pursued, test an amortized, persistent pool with alternating-order trials; do not extrapolate this single batch to all workloads.

Status: awaiting PR CI final-head check and integration review. Not an improved policy model.
