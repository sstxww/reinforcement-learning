# Session s-20261102-2830ac4a — STATUS

- **State:** second/final code-isolation correction submitted; latest valid result pending rerun and CI. Earlier rerun proved extra non-magnetize differences and is not a clean causal ablation.
- **Branch:** `agent/s-20261102-2830ac4a/optimization-001`, base main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **PR:** https://github.com/sstxww/reinforcement-learning/pull/28 (draft).
- **Original run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415008425; seven fully completed TavernGym 1.1.0 games; baseline and candidate ranks [7,8,8] vs [7,8,8], with no verified improvement. Candidate own seed 34200 rank 8, 44 decisions, all eight ranks [8,5,7,1,3,6,4,2].
- **Core correction:** actions 16–22 are **Sell**, 126–195 are **Magnetize** (upstream actions.rs @ fb61201). Old run labeled 'hold_sell' is genuine but did not test selling; must not be cited as sell-policy evidence.
- **Repair:** legacy path `tavern_ai/hold_sell_experiment.py` now houses `AvoidMagnetizePolicy`, reports optional magnetize exposure and shadow baseline disagreements; engine-action-name regression added to branch-scoped Actions. Re-execution evidence pending.
- **Environment:** TavernGym 1.1.0, source hash `6d8712c93022ba11`, 4017/447/245 observe2; source SHA and source-policy hash recorded in receipts.
- **Training:** 0 MaskablePPO steps; deterministic rules only. Model checkpoint absent/not applicable; no candidate promoted to Best.
- **Original JSON receipts:** `experiments/s-20261102-2830ac4a/*.json` with original policy label; corrected run will update receipts under own path, with previous Git revisions preserved.
- **Original evidence artifact:** ID `13127795190`, 30-day retention until 2026-12-02 08:44:36 UTC. This is not model durability.
- **Failure report:** `research/sessions/s-20261102-2830ac4a/failures/001-action-encoding.md`.
- **Next step:** read new workflow logs + real action exposure counts; update report and knowledge proposal; check PR #28 final-head CI. If no exposure, do not assert candidate/baseline functional equivalence on all game states.

- **Corrected first rerun:** https://github.com/sstxww/reinforcement-learning/actions/runs/41416193318 success with action-name checks, seven full games; original baseline and candidate ranks [7,8,8] both, but 1 non-magnetize disagreement occurred on seed 34202 and acceptance seed 34200 also had one.
- **Second isolation fix:** preserve original 85 action cap and fallback tavern Upgrade priority, assert all candidate/control differences are omitted Magnetize actions. Re-evaluation pending.
