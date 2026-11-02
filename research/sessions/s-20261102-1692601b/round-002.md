# R002 — Fixed sell-swap replication across 20 unseen seed/seat pairs

## Research identity and inheritance
SESSION_ID s-20261102-1692601b.
Branch agent/s-20261102-1692601b/optimization-002 from own verified R001 head 534a316970464937e883209a89321e924af87a3c. Main base 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
R001 draft PR https://github.com/sstxww/reinforcement-learning/pull/72 (stack dependency), R001 experiment https://github.com/sstxww/reinforcement-learning/actions/runs/41422157901 successful; R001 PR CI https://github.com/sstxww/reinforcement-learning/actions/runs/41422849526 successful.
R002 code SHA bbc64f699160c0bde2cabdfed810f88b5e205852, real Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41423144155 SUCCESS.
Pinned TavernGym 1.1.0 engine hash 6d8712c93022ba11, observe2 4017/447/245. Sell actions 16..22, Buy 8..15 in official pinned Rust actions.rs.

## Hypothesis and fixed evaluation protocol
R001's four heldout seed pairs were insufficient to promote a claimed -0.25 improvement. R002 predeclared new test seeds 69131..69150 (none used for R001 calibration or evaluation), controlled seat index i modulo 8, unchanged baseline versus locked R001 candidate min_turn=7, sell_slot=first. Explicitly score placements[controlled_seat], not placements[0]. Only legal observed mask, public game turn and own action count enter policy. The seven other seats are real TavernGym scripted bots.
**No retuning, no new neural training, no PPO/optimizer update**: 0 gradient steps, no model weights. This is an independent evaluation of R001's already chosen rule.

## Actual execution and results
All repository tests, pinned engine validation, and 40 entire eight-player games succeeded. All 40 compact 002 receipts validated, none from an incomplete game, no simulator guard, 0 illegal choices. Run 41423144155 (see above). Receipts path experiments/s-20261102-1692601b/002-*.json; exact summary research/sessions/s-20261102-1692601b/metrics-002.json.

Baseline on 20 distinct seed/seat pairs: mean rank **7.50**, top4 0/20, first 0/20, 956 controlled decisions.
Candidate on same 20 pairs: mean rank **7.40**, top4 0/20, first 0/20, 1170 controlled decisions; 59 actual sell-and-buy interventions, 0 orphan sales, 0 safety overrides.
Paired candidate-minus-baseline rank differences:
[0,0,0,-1,0,-1,0,0,-2,0,0,-2,0,0,0,1,-1,2,0,2].
Mean -0.10; wins 5, losses 3, ties 12. Deterministic 10k-resample paired bootstrap percentile 95% interval **[-0.55,+0.35]**, contains zero; exact two-sided sign p on 8 non-ties **0.7265625**. Not evidence of competitive gain.
R001 heldout N=4 mean delta -0.25 was a tiny pilot; do NOT pool selection seeds or treat R001/R002 as a statistically independent model comparison with trained weights.

## Capabilities, failures, storage and judgment
Can complete matches and execute a bounded replacement in any seat. Cannot select weakest warband unit, value shop alternatives, or show improvement over baseline; average rank >7 and top4 rate 0 in both policies. Real tradeoffs are not learned from action masks alone.
No R002 technical failures, retry count zero. No neural checkpoint exists: no model_sha256, no restoration of neural weights. Durable public branch stores executable code, locked parameters, all 58 R001+R002 game receipts, compact reports and test code. Artifacts expire after 30 days.
Recommendation **REJECT direct integration/promotion of the blind first-slot sale heuristic**; retain only as negative/weak experiment. No Arena ranked matches or upstream writes occurred.

## Next credible hypothesis
Use actual TavernGym card_static data and verified observe2 board/shop indexes to estimate public minion values, buffs, keyword synergies and prospective replacement utility. Mechanically verify observations and card IDs with engine tests first. Compare selective value-positive sales against original main baseline and R001 policy on >=20 NEW seat-rotated pairs. Do not run PPO first, do not declare 15000 MMR.

## Reproduction
bash scripts/bootstrap_engine.sh
python -m pytest
python -m tavern_ai.replicate_1692601b --out-dir experiments/s-20261102-1692601b --metrics research/sessions/s-20261102-1692601b/metrics-002.json
