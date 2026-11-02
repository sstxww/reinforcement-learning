# Round 001 — Hero-power timing ablation with real TavernGym

Session: s-20261102-3a93dae9
Branch: agent/s-20261102-3a93dae9/optimization-001
Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
PR: filed after evidence documentation, see GitHub branch's PR.
Hypothesis: from turn 3 onward, spend at most 3 gold on a legal hero power once per turn if at least 3 gold can be reserved.
Changes: unique tavern_ai/hero_power_ablation_s20261102_3a93dae9.py, unique tests and workflow. Shared baseline, PPO, train.yml, canary, evaluator and upstream were not modified.

## Environment and algorithm

Real TavernGym v1.1.0; upstream commit fb61201a557ddd36a411cf44aac51ce4d9b606ce; source hash 6d8712c93022ba11; observe2 patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0. Features 4017, card slots 447, action count 245, legal-mask guarded. Actual simulator vs seven official scripted bots; no fake simulator. Candidate is RULE BASED, not PPO: training steps = 0; model zip/hash = not applicable. Last policy code SHA256: a6aba2d5f349911dfebf568c2fdbae305bf4c1adb07ee23eaef339c80bd72e0a.

## Actual runs and diagnosis

1. Run https://github.com/sstxww/reinforcement-learning/actions/runs/41415703877 — SUCCESS, source commit 7bb35feeb222bf05aefc5bc0615db74ec130b3d4. 23 tests passed. Seeds 18021/18022: candidate placements [8,8], baseline [8,8], candidate hero-power usages [0,0]. This was an INACTIVE pilot, not evidence of skill efficacy. Preserved without combining with later intervention results.

2. Run https://github.com/sstxww/reinforcement-learning/actions/runs/41416155846 — SUCCESS, source commit 82b71762edc35c23b63b0d93c50e9336a37ff5d1. 23 tests passed. 6 candidate and 6 baseline complete games, seeds 18101–18106. Candidate [8,7,7,6,1,7], baseline [8,8,7,7,8,8]. Mean rank 6.00 vs 7.67; paired delta -1.67. Hero-power usage counts [4,8,0,5,12,8]. **Important metadata defect**: receipt policy field still said free_hero_power_once_per_turn although the executed code was the affordable three-gold-reserve variant. Original source commit and receipt code SHA256 edce76c81671d5b51cea3c012f3b0595bf95194afa8ea838b2e1510ff6807c2e prove actual provenance. Do not interpret the stale label literally; original receipts deliberately preserved.

3. Run https://github.com/sstxww/reinforcement-learning/actions/runs/41416624735 — SUCCESS, source commit c371662f26c4286458d9fbb83b8186d356e1ea9f. 25 tests passed. Six independent new candidate and baseline real matches, seeds 18201–18206. Corrected policy label affordable_hero_power_gold_reserve_v2. Candidate [8,8,7,8,8,8], baseline [3,8,7,8,8,8]. Mean 7.83 vs 7.00, paired delta +0.83 (candidate WORSE). Candidate hero-power actions [6,0,0,0,0,6]. Independent batch did not reproduce early gains.

All 28 games (14 candidate + 14 baseline, including pilot) completed genuinely with Game.is_over() true. All candidate receipts record eight placements, seed, decisions, turns, engine hash, source commit, source SHA256, no illegal actions, no truncated combats and no turn-limit termination. Source commit is in git_sha. Seed 18105 (candidate 1 vs baseline 8) is a positive outlier; seed 18201 (candidate 8 vs baseline 3) is a counterexample.

## Aggregation (excluding inactive pilot)

- 12 paired new seeds; candidate mean placement 83/12 = **6.9167**; baseline 88/12 = **7.3333**; paired delta **-0.4167**, lower means better.
- Candidate top-four 1/12 (8.33%), first 1/12 (8.33%); baseline top-four 1/12 (8.33%), first 0/12.
- Active skills used **49** times, in 7/12 games. Five games had no available power, limiting effective sample size.
- Batch-specific paired deltas -1.6667 and +0.8333 conflict. **No validated competitive improvement**; no promotion of this experimental rule into standard baseline.

## Reproduction and files

Executed on GitHub Ubuntu/Python 3.12: install project test deps; pytest; scripts/bootstrap_engine.sh; tavern_ai.contract; then python -m tavern_ai.hero_power_ablation_s20261102_3a93dae9 --seeds 18201 18202 18203 18204 18205 18206. Validated all twelve latest receipts with tavern_ai.validate_receipt. Earlier runs follow their exact logged seeds.

- experiments/s-20261102-3a93dae9/001-SEED.json and baseline-SEED.json for all 14 seeds.
- research/sessions/s-20261102-3a93dae9/paired-results.json (inactive pilot).
- research/sessions/s-20261102-3a93dae9/paired-affordable-results.json (early active set).
- research/sessions/s-20261102-3a93dae9/paired-confirmatory-results.json (fresh confirmation).
- Actions artifacts retained 30 days, not permanent models. Compact receipts tracked in Git; no model checkpoint exists for this rule-only experiment.
- No Arena practice or ranked game, upstream write, shared-model overwrite, forced push or PR merge.

## Decision / next hypothesis

**NOT PROVEN. Do not merge as production strategy by default.** Run more independent seeds stratified by hero choice and power cost/effect; distinguish turns with usable powers from passive heroes. Evaluation must track paired results without selecting favorable seeds. Review remains the responsibility of the human integrator.
