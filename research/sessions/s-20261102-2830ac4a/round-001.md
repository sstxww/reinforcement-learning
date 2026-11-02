# s-20261102-2830ac4a — Round 001: hold-sell baseline ablation

## Research hypothesis and scope
Test whether suppressing the V0 baseline's unconditional sell-before-buy decision improves final placements. The shared baseline checks the 126–195 sell region before the 8–15 buy region, even when buying is legal. The experimental rule only changes this priority: keep mandatory choices, play from hand, preserve the original tavern-tier schedule, buy when legal, then end the turn instead of selling. A 60-action-per-turn safety cap applies when ending is legal.

Scope: `tavern_ai/hold_sell_experiment.py`, `tests/test_hold_sell_experiment.py`, and a session-only workflow. No changes to common training, model, canary, test or evaluator implementations.

## Provenance
- Session: `s-20261102-2830ac4a`
- Experiment branch: `agent/s-20261102-2830ac4a/optimization-001`
- Main base: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Real-engine contract: TavernGym 1.1.0, `observe2`, 4017 float features, 447 indexed cards, 245 legal-masked actions, engine hash `6d8712c93022ba11`.
- Exact upstream commit: `fb61201a557ddd36a411cf44aac51ce4d9b606ce`
- Observe2 patch SHA256: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`
- Training: deterministic rule-policy experiment, **0 PPO timesteps**; no model checkpoint or optimizer state.
- Baseline reference: `tavern_ai.baseline.BaselinePolicy`, not a PPO model.
- Candidate: `tavern_ai.hold_sell_experiment.HoldSellPolicy`; policy source SHA256 is stored in each candidate receipt.

## Execution plan and evidence locator
- Own required complete eight-player candidate match: seed 34200 → `experiments/s-20261102-2830ac4a/001-34200.json` upon success.
- Paired holdout seeds: 34201, 34202, 34203. Control and candidate each face seven official TavernGym bots. Save each individual full-game receipt.
- Real source validation: `python -m pytest`, `bash scripts/bootstrap_engine.sh`, `python -m tavern_ai.contract`, `python -m tavern_ai.hold_sell_experiment --agent-id s-20261102-2830ac4a --seed 34200 --pair-seeds 34201 34202 34203 --out-dir experiments/s-20261102-2830ac4a --report reports/s-20261102-2830ac4a/hold-sell-paired.json`.
- Own Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415008425
- Evidence retention: Actions artifact 30 days; JSON evidence should be committed in session namespace if the job succeeds.

## Historical context and risks
- Public knowledge index has no proven improvement from this sell suppression; hypothesis is new for this session.
- Separate active PRs have tested card pooling, embedding width, reward shaping, entropy, log-feature transforms, purchase-slot selection and insertion placement; their results are not counted as this session's.
- The unbounded raw PPO loop incident and Release 403 are historical; no PPO or Release publishing is attempted here.
- Full-game safety limit is 30,000 outer scheduler iterations. If it fires, do not claim that the game completed.
- A single win or three paired samples cannot establish robust competitiveness, even if average rank improves.

## Outcome / next research question
The exact result must be read from the real workflow and committed receipts. Until then, **no performance improvement is claimed**. If the candidate loses consistently, consider a conditional sell policy (only sell when buying and board constraints warrant it) in an isolated subsequent round. If it improves, expand independent seeds before model promotion.

## Verified execution results (2026-11-02; append-only evidence)
- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415008425 — `completed/success` at code SHA `f6cd60f951be78c67e30c6a717e5d600b05d49d8`.
- Unit/regression tests passed, pinned source contract verified, all candidate/control receipts validated by `tavern_ai.validate_receipt`.
- Mandatory independent candidate match seed 34200: `Game.is_over() == True`, own rank **8**, placements **[8,5,7,1,3,6,4,2]**, 44 decisions, 15 turns, 0 illegal actions, 0 combat truncations and no turn-limit end.
- Held-out seeds 34201–34203: baseline ranks **[7,8,8]**, candidate ranks **[7,8,8]**; both mean placement **7.6667**, first rate **0/3**, top-four rate **0/3**, per-seed deltas **[0,0,0]**.
- Seven complete real eight-seat games total: one independent candidate acceptance match and six paired heldout matches (three per arm). None are Arena matches.
- Candidate policy source SHA256 `0fbedc281a33e4ff5f7c52ddb22e2290db7193c055b1a85f1cccb72c260c481f`; no PPO model or model-weight SHA exists because this was a deterministic strategy ablation.
- Results: `reports/s-20261102-2830ac4a/hold-sell-paired.json`, `experiments/s-20261102-2830ac4a/001-34200.json`, `experiments/s-20261102-2830ac4a/{candidate,control}-{34201,34202,34203}.json`.
- Separate artifact ID `13127795190`, expires `2026-12-02T08:44:36Z`. Evidence JSON also committed to Git; no model checkpoint.
- **Result:** no measured rank improvement; `not proven`. Identical decisions counts/placements warrant testing whether branch-specific sell opportunities actually occurred, rather than assuming the hypothesis was sufficiently exercised.
- Failed run repairs: none required in this round. Existing other-PR CI fault `ModuleNotFoundError: sb3_contrib` is not this session's failure and was not changed.
- No transient files were committed. Source, independent tests, workflow, JSON receipts, summary and docs are retained.
- Suggested next round: instrument `baseline_action != candidate_action` and count legal optional sell opportunities, then evaluate only nonzero-exposure seeds and check for leakage/selection bias.

## Critical action-space correction — 2026-11-02
**The original sell hypothesis was invalid.** The actual pinned upstream `crates/taverngym/src/actions.rs` maps actions 16–22 to `Sell`, and 126–195 to `Magnetize`. The initial candidate never changed selling priority: it skipped optional magnetization, while preserving baseline purchase/turn priorities. The name `hold_sell_experiment.py` is historical and retained to make the original error traceable.

Source: https://github.com/MCG-NJU/AutoTavern/blob/fb61201a557ddd36a411cf44aac51ce4d9b606ce/crates/taverngym/src/actions.rs

Original run 41415008425 still proves 7 real complete games, but **does not test whether selling less improves placement**. Its descriptive equality of [7,8,8] vs [7,8,8] should be understood only as a misnamed magnetize-avoidance pilot. The corrected version adds action-level shadow disagreement and legal magnetization exposure counts, plus checks the engine's action names. Corrected run and updated policy hash must replace the old hypothesis as the authoritative finding; never combine versions as independent evidence.
