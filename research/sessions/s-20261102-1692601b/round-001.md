# R001 — Public-observation sell-and-replace calibrated on real games

## Identity, provenance and historical baseline
SESSION_ID s-20261102-1692601b; branch agent/s-20261102-1692601b/optimization-001.
Base main SHA 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
Executed experiment code SHA f0458b0bc357c83ee10306f798a2667cf91a6bca.
SUCCESS https://github.com/sstxww/reinforcement-learning/actions/runs/41422157901.
Engine TavernGym 1.1.0, source 6d8712c93022ba11, observe2 4017 floats/447 cards/245 actions. Pinned upstream Rust actions.rs: Sell 16–22, Buy 8–15. Main baseline never sells.
Other unmerged PRs cover PPO, BC, refresh, freeze, upgrade, hero power; selected an isolated sell-and-replace hypothesis with no shared-file edits.

## Real game mechanism and policy
Hypothesis: on a full seven-minion board, a single sale followed immediately by a legal purchase can sometimes improve a late-game board. Rule: require seven legal Sell actions, at least one legal Buy, no legal Play/Magnetize, current turn >= threshold, own action count <50. Maximum one sale per turn. Must choose first or last slot, not an inferred weak card. Only the player's observable legal mask, public turn and own action counter enter the policy. No hidden state, future shop, RNG, or opponent hands.

## Actual rule-parameter optimization
Finite four-arm selection. Seeds 49131,49132. Two games each plus two unchanged baseline games, total 10 training games.
- Turn >= 7, first sale: ranks [7,7], mean 7.00, 3 sales.
- Turn >= 7, last sale: [7,8], mean 7.50, 4 sales.
- Turn >= 11, first sale: [7,7], mean 7.00, 0 sales.
- Turn >= 11, last sale: [7,7], mean 7.00, 0 sales.
- Training baseline: [7,7].
Predeclared rule: only arms with actual sale interventions are eligible; select smallest mean rank, then lexicographic tie-break. Chosen turn >= 7, first.
Neural gradient updates = 0; PPO steps = 0. This is real-game discrete policy calibration, not a neural training achievement. No new model.zip or neural SHA256.

## Eight-seat full-game evidence and heldout comparison
18 actual complete eight-seat TavernGym matches (10 train and 8 evaluation); all receipts validated, no simulator combat truncation, turn-limit, illegal selected action, or model safety override. Source run at URL above.
Unseen heldout seeds [59131,59132,59133,59134].
Baseline ranks [8,7,8,7], mean 7.50, top4 0/4, first 0/4.
Candidate ranks [8,7,8,6], mean 7.25, top4 0/4, first 0/4.
Paired candidate-minus-baseline rank deltas [0,0,0,-1], mean -0.25.
Candidate executed 10 sales and 10 follow-up buys, 0 unpaired sales.
Example candidate receipt: experiments/s-20261102-1692601b/001-heldout-candidate-59134.json, place 6, 77 agent decisions, 17 turns, placements [6,5,4,2,3,8,1,7], 3 actual sales.
Matched baseline: place 7, 65 decisions, placements [7,3,5,6,4,8,1,2].
One favorable result across only four paired seeds is NOT evidence of general rank or MMR improvement.

## Reproduction and durability
Strategy: tavern_ai/sell_swap_1692601b.py; tests: tests/test_sell_swap_1692601b.py; finite workflow .github/workflows/sell-swap-1692601b.yml.
Compact result research/sessions/s-20261102-1692601b/metrics.json and real receipts experiments/s-20261102-1692601b/001-*.json. This branch durably saves code/selected rule parameters, but no neural weight checkpoint exists. Artifacts expire at 30 days, Git receipts persist.
Command: bash scripts/bootstrap_engine.sh; python -m pytest; python -m tavern_ai.sell_swap_1692601b --out-dir experiments/s-20261102-1692601b --metrics research/sessions/s-20261102-1692601b/metrics.json.

## Faults, uncertainty, integration and next experiment
No failed steps or retries in R001. Latest PR-head CI must still be checked after PR opens.
Decision: RETEST, not PROMOTE; do not merge a speculative change into shared BaselinePolicy. Four seeds are insufficient and a first-slot sale is not a strength-aware tactic.
Next: estimate board/shop card strength using verified public observe2 slots and card_static data; gate each sale on a demonstrably better replacement and compare against our fixed rule and main baseline over >=20 new seat-rotated seeds. Never infer Arena 15000 from TavernGym ranks.
