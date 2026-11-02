# AutoTavern-AI V4 · s-20261102-13020d89 · Round 001

## Identity / sources
- Start main commit: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Own branch: `agent/s-20261102-13020d89/optimization-001`; implementation commit `9afdc1df057e554cda8f8ec51222c2a06f297bd4`.
- Real 13-match run: https://github.com/sstxww/reinforcement-learning/actions/runs/41422187968 (success; tests, pinned engine, real match/receipt checks, result push).
- Result commit: `a4d94e14e15fcd96cb0284e9d0afd9f0f9f7df6f`.
- Simulator pinned TavernGym 1.1.0; upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; engine hash `6d8712c93022ba11`; observe2 features 4017 / card slots 447 / discrete actions 245. Verify against `tavern_ai/contract.py`.

## Hypothesis / known prior research
Main `BaselinePolicy` prioritizes Play/Buy and upgrades on turns 2,5,7,9,11 without considering own board population and health. Try deferring an otherwise legal planned upgrade in favor of an immediately legal Buy while underdeveloped; use public own health as an emergency gate for later turns. Existing main `reports/evaluation/v1-baseline.json` reported 7.25 mean rank (four separate seeds). Open PR #60 documented PPO non-buy pathology; PRs #61/#62 show BC accuracy is not competitive strength. These are leads, not merged shared knowledge. Different from fixed upgrade-delay PR #35 because intervention depends on live own board count and health, though both test economic timing.

## Real mechanic/source
- Pinned upstream `crates/taverngym/src/actions.rs`: action 3 Upgrade, 8–15 Buy, 30–45 pending Choose, 46–195 Play/Magnetize; all decisions pass actual legal mask.
- Pinned upstream `crates/taverngym/src/obs.rs`: public globals features[5]=own health/40, features[33]=own board size/7. Policy also uses own turn/action count. No opponent hidden hand, RNG, future shop or internal state.
- Rules test in `tests/test_economy_gate_s_20261102_13020d89.py`: mandatory choice priority; mask legality, economy gate, health condition, existing 85-action termination and invalid shape. The isolated Actions job reports successful pytest and real engine fingerprint. The tests' synthetic observation cases check policy logic; full real-game receipts verify deployed behavior and completion, not deep card-effect mastery.
- Safety: the candidate inherits main BaselinePolicy's >=85-action end-turn protection. The number of protection triggers is recorded separately, not represented as raw PPO mastery.

## Algorithm / executed tuning
- New own module `tavern_ai/economy_gate_s_20261102_13020d89.py`, tests, unique 55-minute bounded push workflow. No shared module, upstream or Arena changes.
- Two candidate minimum-board thresholds: 2 and 5.
- Actual parameter-search games: seed 73010 and 73011 for each threshold (4 complete 8-seat games). Threshold 2 rank [6,8], mean 7; threshold 5 rank [6,8], mean 7. Both had 2 upgrade deferrals. No train-seed distinction; deterministic tie-break selected 2.
- PPO environment steps: **0**; neural gradient updates: **0**. This is on-policy real-match, rank-driven finite parameter search, not a neural-weight checkpoint. Strategy config `reports/s-20261102-13020d89/001-policy.json`, SHA256 `12c092e650d8a6be5b803b5e6a50f87763f74cd732ca8135a7a11e4915ed2be8`.

## Authentic full eight-player game evidence
All 13 recorded matches have `Game.is_over()`, receipt schema validation, no engine combat truncation, no turn-limit end, 0 illegal candidate actions and 0 budget-guard forced endings.
- Candidate canary seed 73030, rank **8**, 15 turns, 51 actions, 1 upgrade deferral.
- Heldout paired seeds **73020,73021,73022,73023** were disjoint from training. Unmodified Baseline ranks **[6,6,8,8]** (mean **7.00**); candidate ranks **[5,6,8,6]** (mean **6.25**). Top-4 0% and first 0% in both groups. Pair deltas candidate-minus-baseline **[-1,0,0,-2]**, mean **-0.75**. Candidate 4 deferrals; no guard activations.
- With only n=4 pairs and no top-4, evidence is **not sufficient for a confident strength claim**. Naive paired t CI for rank difference is approximately [-2.27, +0.77]; small sample/discrete placement make interval approximate only.
- Full receipts: `experiments/s-20261102-13020d89/*.json` (13). Compact metrics: `reports/s-20261102-13020d89/001-results.json`. Actual policies and samples are versioned on own branch. No neural weights were created.
- All temporary runtime rollouts and vendor compilation stay out of Git. Release/Artifact is not claimed as a permanent neural checkpoint; small parameter config and receipts are persistent in Git.

## Failures / regression / integration
- Successful engine-backed run, no production incident. Earlier authoring JavaScript had an interpolation syntax error before any GitHub tree/commit; corrected without launching a failed workflow.
- Observed limit: both tuned thresholds acted identically on two train seeds; this training set did not distinguish their behavior. The rank advantage is small-sample and may not repeat. No model promotion.
- Recommendation: **RETEST** for candidate performance; integrate at most isolated policy experiments/tests after review, **not** a shared Champion or replacement for strong strategy. Request more heldout seeds, seat rotations and stronger official-bot reference before policy adoption.
- Do not merge dependent or negative PRs as strength gains; PR #15's V2 PPO 1280 steps showed old/new rank [8,8,8,8] on its four-seed pilot.
- Next hypothesis: explicit public card-value + board-race synergy encoding and teacher labels for shop-card choices. The single simple deferral cannot improve card choice and even the best independent ranks remained outside the top four. Require new true engine capability tests and a stronger teacher.

## Recovery
On this branch: install `pip install -e '.[test]'`; `bash scripts/bootstrap_engine.sh`; `python -m pytest tests/test_economy_gate_s_20261102_13020d89.py`; run `python -m tavern_ai.economy_gate_s_20261102_13020d89` in an isolated environment. This uses the same fixed 13 seeds and overwrites only this session's own receipts. For new independent evidence, edit test seeds in own new optimization round rather than pretending replay is heldout.
