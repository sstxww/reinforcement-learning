# Round 002 — frequency-bounded buy-priority with real upgrade-override counts

## Identity, provenance and hypothesis
- Session: `s-20261102-9c034841` (same independent session as Round 001, no sub-agents).
- Round-002 isolated branch: `agent/s-20261102-9c034841/optimization-002`; base main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Actual evaluated policy commit: `40e8b269998a34ee22eb1957aa8a27a70ff18aaa`; evidence commit: `d843987b84e04a9d0e3d997e15a40a9906c17c63`.
- Successful real GitHub Actions run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416603661
- Round 002 draft review PR: https://github.com/sstxww/reinforcement-learning/pull/48; independent latest-head CI must pass.
- Previous round and CI passed: https://github.com/sstxww/reinforcement-learning/pull/30 ; CI https://github.com/sstxww/reinforcement-learning/actions/runs/41416043342
- Motivation: R001 on different held-out seeds had unverified -0.5 placement delta but candidate decisions mean 54.25 vs baseline 40.0. Hypothesis: limiting planned upgrade-to-buy substitutions from the first 3 own actions to only the first own action per turn should **reduce decision count** without materially harming placement.

## Changes, isolation and real executable
- New session-local `tavern_ai/upgrade_frequency_s_20261102_9c034841.py` defines three separate arms: original unchanged baseline; `planned-buy-first-three-decisions-r001-replay`; `planned-buy-first-decision-r002`.
- Both candidate arms override **only if** unchanged baseline selected legal upgrade action 3 on turns {2,5,7,9,11}, buy (8..15) is legal, and own current-turn action count is inside the 3 or 1 threshold. Higher-priority discover/play choices are preserved.
- Traces actual `upgrade_to_buy_overrides` during own-seat decisions; all steps run via original TavernGym Game/observe2/legal masks and 7 official `bot_play` opponents, not a mocked engine.
- Independent workflow `.github/workflows/experiment-s-20261102-9c034841-r002.yml`, unique concurrency, 80-min job bound, read-only token, 30-day artifact, no auto Git commit or endless triggering. Unique policy and tests only; no shared baseline, main train.yml, upstream or other agents edited.

## Training, engine and tests
- Pure rule strategy tuning; **PPO gradient steps 0**, no weights, no model SHA256, no checkpoint/optimizer and no Best promotion.
- Real pinned TavernGym **1.1.0**, source fingerprint **6d8712c93022ba11**, upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, observe2 4017 float/447 card indices/245 legal actions.
- 29 regression tests passed, pinned engine built and confirmed, 13 complete real eight-seat games, all stages successful.

## Mandatory own candidate game
- Seed **49201**, path `experiments/s-20261102-9c034841/002-49201.json`: candidate is one-decision buy-first policy.
- `Game.is_over()==True`, 15 turns, **41 own decisions**, **3 actual legal upgrade-to-buy overrides**, final rank **8**, full placements **[8,5,1,4,2,7,6,3]**.
- Illegal actions: no error; truncated combats **0**; turn-limit-end **false**. This is genuine candidate-controlled completion, not an earlier baseline or PPO rescue.

## Paired independent new seeds

| Seed | Baseline rank / decisions | 3-decision rank / decisions / overrides | 1-decision rank / decisions / overrides |
|---|---|---|---|
| 49211 | 7 / 49 | 7 / 56 / 3 | 7 / 56 / 2 |
| 49212 | 8 / 33 | 8 / 41 / 5 | 8 / 45 / 3 |
| 49213 | 8 / 45 | 8 / 51 / 5 | 6 / 53 / 3 |
| 49214 | 8 / 69 | 7 / 72 / 4 | 8 / 69 / 0 |

- Complete games: **4 per arm**, 12 held-out + 1 own = **13**.
- Average placement: baseline **7.75**, 3-decision **7.50**, 1-decision **7.25**. Once-minus-three rank deltas `[0,0,-2,+1]`, mean **-0.25**, sample SD **1.2583**. All first-place/top-four rates **0%**.
- Average decision counts: baseline **49.00**, 3-decision **55.00**, 1-decision **55.75**.
- Total genuine tier-to-buy overrides: 3-decision **17**, 1-decision **8** (9 fewer; ~53% fewer). But average decisions **increased by 0.75** compared with the 3-decision arm; original decision-reduction hypothesis **not supported**.
- Same seeds across arms, but different actions change trajectories; n=4, placements near bottom, no proof of quality gain. Do not promote this policy to Best; no model checkpoint exists.

## Receipts and next research
- Original run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416603661
- Genuine JSON receipts: `experiments/s-20261102-9c034841/002-49201.json`, `experiments/s-20261102-9c034841/r002-once-*.json`, `reports/s-20261102-9c034841/r002-three-*.json` and `reports/s-20261102-9c034841/r002-baseline-*.json`.
- Machine-readable summary: `reports/s-20261102-9c034841/round-002-report.json`; entries parsed from original workflow logs and verified for rank permutation, completion, true engine/hash, no truncated combat or turn guard, unique seeds and controlled agent identity.
- Original Actions Artifact ID 13127557959 expires **2026-12-02 08:57:59 UTC**. Compact evidence stored in Git remains reviewable after artifact expiry.
- Round 002 encountered no test/runtime failures. R001 error remains recorded in previous review branch PR #30 and should not be misattributed to R002.
- Proposed next direction: measure board size, upgrade timing, gold and remaining actions per turn on real matched observations before inventing new upgrade heuristics. More held-out seeds needed before competitive claims.
