# Session s-20261102-c0039389 — STATUS

## Round 001 — verified, PR #44 awaiting integration
- Branch `agent/s-20261102-c0039389/optimization-001`, final head `31adcfe4589df5a419b8c8ce052019d63c1dbc90`; open Draft PR https://github.com/sstxww/reinforcement-learning/pull/44 .
- Seven real complete TavernGym eight-seat games. Canary controlled seat4 seed45600 rank4, 67 decisions; baseline seed pairs seat0 [8,8,8] vs seat4 [7,7,4].
- Real run SUCCESS: https://github.com/sstxww/reinforcement-learning/actions/runs/41416587540 ; latest-head PR CI SUCCESS: https://github.com/sstxww/reinforcement-learning/actions/runs/41417526101 .
- Training steps: 0, checkpoint: null, no Best promotion.

## Round 002 — real-engine experiment successful, PR pending
- **Status:** `completed_experiment_pending_pr_ci`.
- **Branch:** `agent/s-20261102-c0039389/optimization-002`, forked from our own R001 head `31adcfe4589df5a419b8c8ce052019d63c1dbc90`. Original main anchor `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`. R002 explicitly depends on R001 PR #44 and must not be integrated first.
- **Run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41418165218 — **SUCCESS**. Run source SHA `7274a19d2af94e1e1db7568f88cc7024d509b5c1`, evidence-committed SHA `e585cb00863740eadd4a3046ef9a704e17c5f491`. Full tests, genuine engine pinned bootstrap, 33 complete real matches, JSON integrity gates, Artifact upload, namespaced evidence commit all succeeded.
- **Engine:** TavernGym 1.1.0, source hash `6d8712c93022ba11`; observe2 4017/447/245. Original unmodified BaselinePolicy SHA256 `e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac`.
- **Mandatory own R002 game:** seed `45720`, controlled seat `7`, rank `8`, decisions `34`, 17 turns; eight placement vector `[4,5,3,2,7,6,1,8]`. `Game.is_over()==True`, illegal actions `0`, combat truncation `0`, game turn guard `false`. Receipt: `experiments/s-20261102-c0039389/002-45720.json`.
- **Held-out seat sweep:** 4 new seeds `45721..45724` × 8 seats = 32 genuine complete games. Mean rank by controlled seats 0–7: `[7,5.75,8,7.25,7,7.75,7.25,7.25]`. Seat0 per-seed ranks `[8,6,7,7]`; seat4 `[6,7,7,8]` (both mean 7, **R001 seat4 advantage did not replicate**). Every one of four seeds had a nonidentical rank pattern across seats, ranges `[2,5,1,3]`. Only seat1 had a top-four result (rank 3) in 32 games; first rate 0/32.
- **Evidence:** `reports/s-20261102-c0039389/seat-sweep-r002.json` and `experiments/s-20261102-c0039389/sweep-*.json`. 33 new receipts. Combined R001+R002 = 40 independently executed real complete games, excluding separate CI canaries.
- **Interpretation:** seat-conditional observed performance is unstable across new seeds and may reflect hero allocations, opponents, turn/action order, not a pure causal seat advantage or policy improvement. All arms use exactly the same untouched policy.
- **Gradient training steps:** `0`; no model checkpoint or Best/Latest promotion. Artifact `13128209144` expires `2026-12-02T09:10:07Z`; compact receipts are already committed.
- **Faults:** no R002 failures, no repairs needed. No Arena activity.
- **PR:** create an R002 PR to main as a dependent/stacked research PR, verify final-head `CI - full-match gate`, do not merge without integration review.
- **Next:** recommend seat × seed stratified evaluation and research hero allocation confounding before promoting new PPO models. Do not extrapolate the first-round n=3 seat advantage.
