# Session s-20261102-8555759e — Round 001

**Status:** completed experiment; negative result; awaiting PR review.  
**Research question:** Does the positional tie-break among legal choice actions 30–45 affect full-game results?  
**Hypothesis:** A fixed first-legal-choice preference may bias decisions; selecting the last legal choice could change outcomes. This is a screening experiment, not a proposed production replacement.

## Source, isolation, and preconditions

- **Main base SHA:** `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **Independent branch:** `agent/s-20261102-8555759e/optimization-001`.
- **Workflow source SHA:** `0ac6a59d864ced94179b90a031209d2ade45d749`.
- **Executed workflow:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415719754 (success).
- **Recorded real-match commit:** `03607dcb8f7897ea0224e2aab261eda325fafd76`.
- **Engine:** TavernGym 1.1.0; source hash `6d8712c93022ba11`; upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; checked patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- **Observation/mask:** observe2 4017 float features, 447 card indices, 245 legal actions; all were checked in live games.
- **Concurrent PRs checked:** reward shaping, PPO network, entropy, upgrading, purchase slot, refresh, early selling, and board placement were active. No preexisting open PR titled for this choice-index tie-break experiment. Only new isolated module, test, workflow, own reports, and own receipts were changed.
- **Existing experience:** PR #9 and #15 have genuine PPO and checkpoint experiments, but no confirmed strength gain. The main knowledge index has no merged round reports.

## Modification and validation

- Added `tavern_ai/experiment_s_20261102_8555759e.py`: wraps the unchanged BaselinePolicy, selects the **highest indexed legal action** only if actions 30..45 are available, and otherwise delegates decisions unchanged. Both arms use identical seeds against seven official scripted bots.
- Added `tests/test_discover_choice_8555759e.py`: multi-option, singleton, original-policy parity, invalid mask regression tests.
- Added isolated bounded push-triggered workflow, with distinct concurrency group and 40-minute timeout. The workflow was subsequently limited to experiment code/test/workflow changes to avoid re-running on documentation updates.
- **Actual unit result:** 25 tests passed.
- **Actual training:** 0 model/PPO steps. This is a *pure rule-strategy ablation*, not neural model training.
- **Policy source SHA256:** `b441dd7f08eb3e95f0e93c69b3e2656bdbb11d17ffdbaad7ee41d747e56c4fed`.
- **No model checkpoint:** not applicable; `model_sha256=null`. No change to Best, Candidate, or Latest weights.

## Genuine eight-seat matches

Execute on real pinned engine:
`python -m tavern_ai.experiment_s_20261102_8555759e --games 6 --start-seed 855570`

The workflow verified all 12 emitted receipts using `python -m tavern_ai.validate_receipt`. All 12 games genuinely reached `Game.is_over()`, with 0 illegal actions, no truncated combats, and no turn-limit guard. Each receipt includes placements for eight seats and actual controlled decision count. No result was simulated or pre-filled.

**Mandatory candidate-owned receipt:** `experiments/s-20261102-8555759e/001-855570.json`; seed 855570; controlled rank 8; all seat placements `[8,3,4,5,7,1,6,2]`; 16 turns; 49 controlled decisions; 11 alternatives selected; complete and guard-free. Workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41415719754.

All candidate receipts: `experiments/s-20261102-8555759e/001-{855570..855575}.json`; baseline receipts: `experiments/s-20261102-8555759e/baseline-{855570..855575}.json`. This repository's `reports/s-20261102-8555759e/round-001.json` is the compact actual results summary.

| Seed | Baseline rank | Last-choice rank | Candidate minus baseline |
| --- | ---: | ---: | ---: |
| 855570 | 8 | 8 | 0 |
| 855571 | 3 | 8 | +5 |
| 855572 | 8 | 8 | 0 |
| 855573 | 5 | 8 | +3 |
| 855574 | 6 | 8 | +2 |
| 855575 | 8 | 8 | 0 |

- **Baseline:** 6 games; average rank **6.333**; first place **0/6**; top four **1/6**; 43 choice actions, none changed from first-index selection.
- **Candidate:** 6 games; average rank **8.000**; first place **0/6**; top four **0/6**; 53 choice actions, all 53 chose an alternative to first-index selection.
- **Paired delta (candidate minus baseline):** **+1.667 rank positions** (higher is worse).
- Different counts of choice actions are expected after divergent game trajectories; they are not treated as independent observations.
- Six seed-pairs are a screening sample. These results do not establish a population-level causal mechanism or an Arena Elo change.

## Conclusion, failures, and risk

**Negative result.** Always selecting the last available choice yielded no wins, no top-four finishes, and worse or equal final placement on each of six seeds. **Do not promote the candidate to Best or use it as production strategy.** Preserve the working baseline. Hypothesis that last-index selection can improve results is unsupported by this pilot.

No code/test/game or Actions error occurred during this round. The independent workflow finished successfully. Its uploaded Artifact is a **30-day temporary backup**, not persistent checkpoint storage; textual experiment metrics and 12 original JSON receipts are committed in Git. No caches, models, rollouts, or large logs were committed.

## Next bounded hypothesis

An action index alone lacks card value information. A follow-up should examine whether the choice range represents hero/discover option types and condition the tie-break on observable candidate identity or board synergy. It should first verify the TavernGym action semantics and then use held-out paired seeds; it must remain opt-in and not modify shared baseline. Do not repeat the same fixed-last strategy as though this failure were inconclusive for the tested six seeds.
