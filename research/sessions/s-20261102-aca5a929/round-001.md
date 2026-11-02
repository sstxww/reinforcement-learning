# Round 001: Public-card purchase-target preference (independent session)

## Identity and provenance
- SESSION_ID: `s-20261102-aca5a929`
- Base: `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Branch: `agent/s-20261102-aca5a929/optimization-001`
- Upstream pinned TavernGym commit: `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, observe2 patch SHA256: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Engine source hash expected: `6d8712c93022ba11`; catalog SHA256 expected: `c4c42e6ce5060e1b79fbcd5f4edbf6d17495f0f52690072481d690610f7ef6d7`.
- No upstream, main, public Champion, other session, or Arena writes.

## Inherited evidence and conflict avoidance
- Read main AGENTS, architecture, background, session protocol, closed loop and historical incidents.
- Open PRs #61-64 attempt teacher imitation; other PRs study freeze, refresh, upgrade, hero power, seating and PPO. None is treated as validated/main.
- Primary known weakness: V0 Baseline always selects first legal shop buy (action 8–15); weights-only PPO can loop and has not established strong results.

## Mechanism and falsifiable hypothesis
- Upstream `crates/taverngym/src/actions.rs` encodes `Buy(shop slot i)` as `8+i` and masks unaffordable/illegal shop items.
- `crates/taverngym/src/obs.rs`: observable `cards` stream includes own board [19:26], hand [26:36], visible shop [36:44]; opponents' private cards are not used. Must reverify dynamically against `taverngym.layout()`.
- `taverngym.card_static()` maps card embedding index to minion kind, tier, base attack/health and race bits [15:26]. These are public static facts; game effects and unknown future cards are NOT predicted here.
- Hypothesis: replacing only **which legal minion shop slot to buy** based on public stats, tribe overlap and exact-pair count changes and potentially improves true eight-seat placements vs unchanged first-slot Baseline.
- Null: no improvement; this project is strategy selection, not full game understanding.

## Bounded optimization and validation
- Implemented unique `tavern_ai/card_synergy_aca5a929.py` and `tests/test_card_synergy_aca5a929.py`.
- Finite parameter candidates: (race,pair) = (0,0), (0.7,0), (1.8,0), (0.7,3.5); common stat=1.0, tier=0.5.
- Training seeds: 79110,79111, 2 complete eight-player matches per candidate (8 true games, 0 PPO/gradient steps); choose lowest training mean placement, tie -> first.
- Held-out comparison seeds: 79220–79223, baseline and frozen candidate on the same seeds (8 true games). Four pairs are **not** enough for strong improvement claim.
- Exact engine, action-mask legality, full completion, no truncation/turn-limit, guard-trigger count, buy-choice override count, checkpoint SHA256, separate training/heldout receipts recorded.
- Workflow: `.github/workflows/experiment-s-20261102-aca5a929.yml`; push paths restricted to own code/workflow, 75m limit, isolated concurrency group. Only own tiny checkpoint and receipt files committed. No auto-merge.
- Full reproducer after engine bootstrap: `python -m pytest tests/test_card_synergy_aca5a929.py`; `python -m tavern_ai.card_synergy_aca5a929 --run`.

## Final real execution: negative pilot
- First run [41421892518](https://github.com/sstxww/reinforcement-learning/actions/runs/41421892518) failed before completing any training match due to an incorrect old/observe2 card-length assumption; see `failures/001-observe2-legacy-layout.md`.
- Repaired code `2fd46064290c772e79318fbe75c442ff31851506`, then [run 41422373796](https://github.com/sstxww/reinforcement-learning/actions/runs/41422373796) **SUCCESS**: unit tests, pinned true engine, actual 8 training matches, actual 8 heldout matches, receipt validation, SHA256 validation and branch-scoped results commit all passed.
- 4 grid candidates × 2 training seeds = **8 genuinely completed games**, PPO steps **0**, gradient optimizer updates **0**; training mean ranks: `[6.5,7.0,7.0,7.0]` (n=2 per arm). Frozen selection index 0: stat=1, tier=0.5, race=0, pair=0. Thus neither added tribe overlap nor pair signal was selected.
- Heldout seeds **79220–79223** (4 paired games): Baseline ranks `[6,8,8,7]`, mean **7.25**, top4 **0%**, first **0%**; chosen candidate ranks `[8,8,7,6]`, mean **7.25**, top4 **0%**, first **0%**. Candidate minus Baseline paired deltas `[+2,0,-1,-1]`, mean 0; no evidence of gain.
- Candidate changed **31 buy target decisions** across four heldout matches; all four candidates and four Baseline games completed, no invalid masked decisions, no combat truncation or time-limit ending; candidate's explicit baseline inherited 85-action guard triggered **0** times in heldout runs.
- Parameter checkpoint `reports/s-20261102-aca5a929/001-weights.json`, SHA256 `971acb6755401e700b26caf251d390903df4fbb67cf1b6015e956b270439bcc4`; only a tiny interpretable JSON weight set, **not** a trained neural network. Run-validated SHA256 and checkpoint format; independent cold-start policy replay not yet measured.
- All genuine 16 receipts and compact metrics persisted in `experiments/s-20261102-aca5a929/` and `reports/s-20261102-aca5a929/001-results.json` on own branch. Temporary artifact also recorded by Actions; no dependence on it for the tiny checkpoint.
- Engine: pinned 1.1.0, source `6d8712c93022ba11`, 4017/447/245, catalog SHA256 `c4c42e6ce5060e1b79fbcd5f4edbf6d17495f0f52690072481d690610f7ef6d7`. Live engine verified 124-legacy-card prefix of 447-slot observe2; the original synthetic test had missed this incompatibility.

## Decision gate and integration advice
**REJECT as a competitive upgrade**: n=4 does not establish an advantage, and the selected configuration disables the new synergy terms. This is a negative pilot, not proof tribe features are worthless in general. Keep mechanism compatibility regression, reproducible harness and failure note for possible integration review; no shared Baseline/PPO/Champion changes.



## Next hypothesis
If ranking changes buys but not placements, inspect action traces to test whether raw stats/tribe similarity correlate with midgame survival; compare stage-conditioned teacher labels, rather than increasing PPO steps.
