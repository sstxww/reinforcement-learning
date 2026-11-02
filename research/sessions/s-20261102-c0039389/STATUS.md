# Session s-20261102-c0039389 — STATUS

## Current state
- **Research status:** `completed_for_review`. PR #44 is open for integrator review; branch CI at `c90a12b2ea5b4bf996364e5ba4aa827b9b8e86c2` passed. Recheck CI after final evidence-documentation commit.
- **Branch:** `agent/s-20261102-c0039389/optimization-001`, based on main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **Evidence commit:** `f201284469f777a9dec0fe80f206a461c9dbb100` (bot-committed independent receipts and report).
- **Successful Actions:** https://github.com/sstxww/reinforcement-learning/actions/runs/41416587540; triggered SHA `4f775d7edab7114a17a740f864d26777b308c72f`; all steps successful, including all repository unit tests, pinned engine bootstrap, 7 genuine full matches, evidence upload and evidence commit.
- **Engine:** TavernGym `1.1.0`, source hash `6d8712c93022ba11`; observe2 4017 floats / 447 cards / 245 actions; real engine verification succeeded.
- **Policy:** original unmodified V0 `BaselinePolicy`; SHA256 `e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac`. No learned model, no PPO gradient steps (`0`), no checkpoint, no new Best/Latest promotion.
- **Own independent full game:** seed `45600`, controlled seat `4`, rank `4`, 67 decisions, 17 turns; final placement vector `[3,1,8,6,4,2,5,7]`. `Game.is_over()==True`, no illegal actions, combat truncation or end-of-game safety guard. Receipt `experiments/s-20261102-c0039389/001-45600.json`.
- **Held-out paired evaluation:** seeds `45601,45602,45603`; seat-0 original baseline ranks `[8,8,8]` (mean `8`, top4 `0/3`, first `0/3`); same baseline controlling seat-4 ranks `[7,7,4]` (mean `6`, top4 `1/3`, first `0/3`). 6 complete paired games; all seven game receipts have matching controlled seat/rank and eight-place permutations. Full data `reports/s-20261102-c0039389/seat-comparison.json`.
- **Interpretation:** demonstrated sensitivity to controlled seat under these three seeds; seat changes hero allocations, opponent schedule and action order, so **not causal proof** of seat advantage and **not a policy improvement**. Larger stratified evaluation needed.
- **Evidence retention:** full compact receipts and report committed on branch; workflow artifact `13127922958` expires at `2026-12-02T08:57:41Z` (30-day TTL); no model storage implied.
- **Faults:** no failures in this run; no repair needed.
- **PR:** https://github.com/sstxww/reinforcement-learning/pull/44 (Draft; not merged). Successful PR full-game CI on evidence head: https://github.com/sstxww/reinforcement-learning/actions/runs/41417091572. A final docs-only commit requires latest-head CI re-verification.
- **Next research direction:** quantify seat/hero interactions across all eight seats and more independent seeds, or implement seat-stratified metrics before Best promotion without changing shared modules.
