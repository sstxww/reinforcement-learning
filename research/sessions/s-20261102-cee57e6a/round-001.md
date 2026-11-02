# Round 001: public-board swap, genuine negative result

## A. Research identity and background
Session: s-20261102-cee57e6a. Main base: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d. Independent branch: agent/s-20261102-cee57e6a/optimization-001. Evidence workflow and all writes restricted to own namespace; no main, upstream, other agent, Arena or common policy modified.

Audited README, AGENTS, PROJECT_BACKGROUND, ARCHITECTURE, SESSION_PROTOCOL, CLOSED_LOOP, research/knowledge, baseline, canary, evaluation, PPO, workflow, open PR and model releases. Main baseline on older seeds 24000–24003 showed [7,6,8,8] (mean 7.25). Unmerged PR #15 trained a 1280-step PPO candidate with four held-out rank-8 outcomes; it is not a Champion. Numerous concurrent BC/PPO/Freeze/Buy-first experiments are unmerged/unproven.

## B. Mechanism knowledge and test boundary
Pinned AutoTavern upstream fb61201a557ddd36a411cf44aac51ce4d9b606ce plus verified observe2 patch; TavernGym 1.1.0, hash 6d8712c93022ba11, floats[4017], cards[447], masks[245], card vocabulary 3984. Rust actions.rs Sell 16–22, Play 46–125, Magnetize 126–195. obs.rs global[33] = own board length / 7, global[34] = own hand length / 10; board stats offset68 width31, hand offset285 width40. Tests confirmed those against actual real-game own state. Policy reads exclusively own observe2 float features, legal actions, own turn/action count, never hidden opponent data. Driver uses debug Game.view(0)["me"] only for test oracle, never as a policy input. Golden board minions protected.

## C. Hypothesis, algorithm and training configuration
Baseline never deliberately sells. Test whether selling the visibly weakest non-golden minion on a seven-slot board, to make room for a stronger first-hand minion, improves rankings. One swap max per turn, turn >=6, preserve legal pending-choice, play/magnetize and scheduled upgrade priority. Score = public attack+health plus shield/reborn/venomous/taunt crude weights; ignores battlecry, scaling synergies and strategic pivot value.
Training method: bounded *real-game rule hyperparameter search*, not gradient training. Three margins 4/8/12, train seeds 73011 and 73012; frozen selection based only on train rankings, ties choose most conservative margin. Actual PPO steps **0**. Neural model checkpoints **none**. Code SHA256 58e1b1efaf73508743e41371982780ebf7269dd57e37d71dea40e42bbc26751c.

## D. Genuine execution evidence
Successful Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41423127192 passed unit tests, pinned engine install, exact 15 full eight-player games and receipts validator. All JSON game receipts: experiments/s-20261102-cee57e6a/*.json; compact authentic results: reports/s-20261102-cee57e6a/001-results.json.
- Train baseline ranks [8,8], N2, 0 swaps. Margin4 ranks [8,8], 3 actual swaps; margin8 [8,8], 0 swaps; margin12 [8,8], 0 swaps. Selected margin12, training dataset eight real games (2 baseline + 6 candidate).
- Mandatory candidate receipt experiments/s-20261102-cee57e6a/001-mandatory-73029.json, seed73029, full placements [8,3,6,7,2,4,1,5], own rank8, 15 turns, 38 decisions, 0 swaps, 0 forced ends, 0 combat truncation, no simulator turn limit; Game.is_over true.
- Heldout seeds73031–73033, baseline ranks [7,8,8], candidate ranks [7,8,8]. Mean 7.6666667 in each arm; top4 0/3 and first 0/3 in both. Paired candidate-minus-control deltas [0,0,0]; 0 candidate swaps; 0 illegal moves; no combat truncations or turn-limit ending. Six heldout full games. Total successful run complete games: **15**, including mandatory own candidate.
- Interpretation: conservative selected candidate never actually changes the baseline on heldout states. No gain demonstrated. Do NOT claim high-level competitiveness, PPO advancement, 15000 MMR, or a new Best.

## E. Failures and fixes
First run https://github.com/sstxww/reinforcement-learning/actions/runs/41422165613 failed: Python PyGame has no .players (Rust-internal field). Fix driver test oracle to supported Game.view(0)["me"]. Second run https://github.com/sstxww/reinforcement-learning/actions/runs/41422715265 failed: hand-size feature one index off; global feature index32 is gem_hp, index33 board size, index34 hand size. Fix offsets and add tests. Third attempt succeeded https://github.com/sstxww/reinforcement-learning/actions/runs/41423127192. Exactly 2 substantive fixes; no claim of candidate success in earlier failed runs. Detailed incident: failures/001-python-binding.md.

## F. Handoff, integration and promotion
Promotion verdict: **REJECT** selected policy: 0 action interventions and paired mean placement delta 0 on 3 unseen seeds. This is a negative, small-sample experimental result; not proof that all selling strategies are harmful. Do not merge this rule heuristic into baseline from this evidence. No neural checkpoint needed; reproducible pure source and threshold12 are committed. Model sha256 N/A; policy-source sha256 as above. All source, rules provenance and real receipts persist in Git, not dependent on temporary Actions artifacts.
Next proposal: first instrument public full-board/strong-hand event frequencies across new seeds; if rare, prioritize early economic purchase/upgrade timing and teacher policy quality rather than speculative more PPO steps.

## G. Reproduction
With Python 3.12 and own branch checked out, install editable .[test], run pytest tests/test_research_cee57e6a.py, bootstrap via scripts/bootstrap_engine.sh, then python -m tavern_ai.research_cee57e6a --output <fresh-dir> --report <fresh-report>.json. Use fresh output paths to avoid replacing committed evidence; validate real receipts via python -m tavern_ai.validate_receipt.
