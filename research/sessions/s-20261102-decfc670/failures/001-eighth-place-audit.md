# Rank-eight diagnosis, evidence threshold before any further PPO expansion

**Session:** s-20261102-decfc670. **State:** preliminary diagnostic synthesis from prior authentic experiments, not this session's independent PPO game. Do not promote it to proven root cause.

## Available true-game evidence

1. PR #60 / Actions #41418438337: TavernGym 1.1.0, engine fingerprint `6d8712c93022ba11`, seeds 42174-42176, three eight-seat games per 256-step checkpoint. Candidate learning rate 1e-4: ranks [8,8,8], **0 buy actions / 36 total**, **21 model-selected END_TURN / 36**, zero safety-forced END_TURN. Reference 3e-4: ranks [8,8,7], **20 buy actions / 875 total**, **21 safety-forced END_TURN**, largest repeated same-action streak **40**. Difference +0.333 mean placement candidate minus reference (worse), n=3 per arm.
2. PR #15 / Release `v2-learning-41413557445`: 1280 total steps and 4 heldout model matches report [8,8,8,8], with original model [8,8,8,8] and baseline [7,6,8,8]. Published SHA256 is recorded in `models/registry.json`; this session has not yet independently run it.
3. PR #43, now integrated, shows baseline rank [8,8] at seat 0, [7,7] at seat 3, [8,8] at seat 6 across only two seeds and three seats: all results poor. Do not infer intrinsic causal seat advantage.

## Observed facts versus unverified hypotheses

- **Confirmed descriptive symptom:** the measured low-LR candidate executed zero Buy action IDs in three complete games, while selecting END_TURN frequently.
- **Not yet confirmed:** whether Buy was legal and affordable before the END_TURN actions, or whether free/mandatory actions forced that action distribution. A count of zero buys alone does not prove systematically missed purchasing opportunities.
- **Separate symptom:** the reference selected 788 raw actions outside the coarse Buy/Play/End/mandatory categories and reached 40 identical repeated actions; their semantic identity and state-effect have not been established.
- **Unproven causes:** changed learning rate, insufficient samples, card encoding, reward scale, wrongly masked actions, too-short effective horizon, action loops, weak baseline, and environment distribution shift. These are hypotheses to test, not facts to assert.
- **No claim of model improvement:** models in these two studies did not achieve a demonstrated top-four gain. No reliable Champion identified.

## Falsifiable next experiment

Instrument a pinned current checkpoint with exact state-action telemetry on NEW heldout seeds:
- For every model decision: `turn`, phase, `gold_before`, `legal_buy_count`, `affordable_buy_count`, `legal_end_turn`, `chosen_action`, `chosen_family`, `guard_forced`, hash of `observe2` features+cards before/after and whether simulation progressed.
- Per turn: consumed/unused gold, purchase count, Play count, board count, tavern upgrades, refresh count; separate model-selected END from safe forced end.
- Record **purchase opportunities missed** only when Buy was both mask-legal and affordable and END_TURN was model-selected, with proper Game state interpretation; no hidden opponent data in policy.
- Match seed, seat, opponent recipe and checkpoint SHA256 for Baseline, old and candidate; use at least exploratory replicated pairs before interpreting gain.
- Isolate and test ONE intervention (e.g. action mask correction only if a demonstrable mismatch exists), and run real complete games before changing any Champion pointer.

## Current session boundaries

This branch validates model archive integrity first. Own new PPO gradient steps: **zero**; raw PPO gameplay telemetry: **not yet independently collected**. Baseline real-game CI is separately labelled and does not prove any model capability. Do not claim model recovery or rank-eight root cause until those separate tests actually pass.
