# Round 001 — Mandatory-choice tie-break: verified paired real games

## Identity and hypothesis
- Session: s-20261102-9c463177
- Base main SHA: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Branch: agent/s-20261102-9c463177/optimization-001
- Hypothesis: choosing rightmost instead of leftmost among simultaneous legal mandatory-choice actions [30,46) changes real full-game outcomes, possibly improving rank.
- Isolation: only new session-specific script, test, workflow, files; **no shared module edits**.

## Historical evidence considered
- Read main shared knowledge/incident playbook and open PRs. In particular #22 and #23 measured architecture or shaping on true small PPO runs with no proven rank improvement; #6 contains lessons from mismatched tests and baseline strategy. Our ablation tests a different tie-break mechanism.
- Another session upgrade experiment (run 41415062300) failed 2 logic-expectation tests before gameplay; this is not our own test failure.

## Exact engine and code
- TavernGym 1.1.0, upstream fb61201a557ddd36a411cf44aac51ce4d9b606ce; runtime source hash 6d8712c93022ba11.
- Verified observe2 dimensions 4017 floats, 447 card IDs; 245 legal-masked actions.
- Patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
- Runner scripts/choice_tiebreak_s-20261102-9c463177.py
- Runner SHA256 694993624ff33bd9564463e9c08a673bf080d819cfbbda461ebbe786d5f202bd
- Tested source SHA 9c6e97b9717fd3113a158444c56ae27d780d3d74
- Test tests/test_choice_tiebreak_s-20261102-9c463177.py; all unit tests in workflow passed.
- Successful isolated GitHub Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41415579630
- Reproduction: python scripts/choice_tiebreak_s-20261102-9c463177.py --start-seed 39001 --games 4

## Training / checkpoint
This is a **pure rules-policy experiment**. Actual PPO training steps **0**; no PPO hyperparameters used, no model checkpoint produced, and no new Best model. Unlike PPO experiments, training is not required for this strategy ablation.

## Full eight-seat competition
Each candidate and baseline directly controlled seat 0 against seven official TavernGym bots, and each of the eight games ran to Game.is_over() via tavern_ai.canary.run. All eight candidate/baseline receipts were committed to experiments/s-20261102-9c463177/. Seed 39001 candidate receipt 001-39001.json: rank 8, **38 own decisions**, 14 turns, 0 truncated combats, no turn-limit end, completed true, model hash null (rule strategy).

| Seed | Main baseline rank | Candidate rank | Candidate - baseline |
|---|---:|---:|---:|
| 39001 | 5 | 8 | +3 |
| 39002 | 8 | 7 | -1 |
| 39003 | 7 | 6 | -1 |
| 39004 | 7 | 5 | -2 |

- Baseline: n=4, mean rank 6.75, first rate 0%, top-four rate 0%.
- Rightmost mandatory candidate: n=4, mean rank 6.50, first rate 0%, top-four rate 0%.
- Paired mean rank delta: -0.25 (smaller rank is better).
- Across four candidate games, **21 actual changed decisions**, 21 multiple-choice events.
- No observed invalid-action exceptions, no truncated combats, no engine turn-limit guards in the successful full-match run. Every record is actual canary.run output, not a mock.
- The intervention was measurably active, but n=4 is too small to infer a playing-strength gain; changed choices may alter downstream RNG. **Status: no verified improvement**.

## Results, failures, persistence
- Exact JSON metrics research/sessions/s-20261102-9c463177/round-001-metrics.json.
- Mandatory candidate receipt experiments/s-20261102-9c463177/001-39001.json.
- Additional comparison receipts baseline-39001..39004.json and candidate-39002..39004.json.
- The successful workflow installed the pinned engine, ran pytest, completed eight true games and committed all results. No repair attempt was needed; no private checkpoint to persist.
- GitHub source and JSON receipts are durable as repo commits; workflow Artifact is only a 30-day backup, not permanent model storage.
- Main remains untouched. No official ranked TavernArena activity.

## Next hypothesis
Do not use a blind last-option tie-break as a stronger default. Next investigate **choice-option semantics and cards**, then evaluate contextual utility over at least 30 independent paired seeds, checking for real interventions and confidence intervals. Do not promote unverified strategy or checkpoint.
