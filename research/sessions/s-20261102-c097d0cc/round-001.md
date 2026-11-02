# Round 001 — rightmost placement ablation

- Session: `s-20261102-c097d0cc`
- Start: `main@6ac59235b8238196a0e6462de77b72413c829372`
- Branch: `agent/s-20261102-c097d0cc/optimization-001`
- Hypothesis: for the *same first playable hand slot*, choosing the rightmost legal board insertion slot instead of the leftmost changes attack order and could improve mean finishing rank.
- Prior work: main README, AGENTS, PROJECT_BACKGROUND, SESSION_PROTOCOL and knowledge index. Four open, unmerged PRs cover economy, learning, evaluation and infrastructure; no merged main session evidence existed at kickoff. Their observations are not treated as verified improvements.
- Changed code: new `tavern_ai/placement_probe.py` and `tests/test_placement_probe.py`; no change to shared `baseline.py`, `canary.py`, or training files.
- Reproduction: `python -m tavern_ai.placement_probe --agent-id s-20261102-c097d0cc --seed-start 31001 --games 20`.
- Environment: genuine TavernGym 1.1.0, source fingerprint `6d8712c93022ba11`, upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`; observe2 floats 4017, cards 447, mask 245.
- Tuning budget: 20 fixed seed pairs (40 full eight-seat matches), gradient PPO training steps **0**. This is a discrete strategy-parameter ablation, not PPO weight training.
- Execution: https://github.com/sstxww/reinforcement-learning/actions/runs/41413715459
- Controlled candidate first match: `experiments/s-20261102-c097d0cc/001-31001.json`; full results and control receipts in the same session folders.
- All game receipts were generated from `canary.run` using `Game.is_over()` and validated with `validate`; masks are tested before each step. Games reaching engine-protective truncation would fail validation.
- Ranks (seat 0, lower better): control `[8, 8, 8, 8, 5, 7, 8, 7, 7, 5, 8, 5, 7, 8, 7, 8, 8, 7, 8, 6]`; candidate `[8, 1, 8, 8, 7, 7, 8, 7, 6, 8, 8, 8, 6, 7, 8, 8, 7, 7, 8, 6]`.
- Mean rank: control **7.150**, candidate **7.050**; candidate-control delta **-0.100** (better descriptively).
- Top-four: control 0.0%, candidate 5.0%; win: control 0.0%, candidate 5.0%.
- Paired deltas: `[0, -7, 0, 0, 2, 0, 0, 0, -1, 3, 0, 3, -1, -1, 1, 0, -1, 0, 0, 0]`; sample is too small to infer a true strength gain. Seeds may remain noisy despite pairing.
- Action count: control `[57, 68, 36, 48, 55, 65, 46, 50, 52, 56, 30, 57, 37, 52, 46, 39, 34, 49, 39, 53]`, candidate `[55, 55, 34, 37, 48, 64, 45, 45, 47, 36, 32, 44, 41, 45, 40, 42, 43, 48, 43, 56]`; simulator protective truncations: control 0 / candidate 0; illegal actions 0 by checked-mask execution.
- Artifacts: compact receipts + comparison.json committed; no model or checkpoint created; temporary engine build and pip caches excluded from Git.
- Failure modes: changing only insertion position may not fix weak card valuation and economy; composition-dependent effects are unmodeled. No actual TavernArena ranked games.
- Next step: validate on 30+ fresh paired seeds with bootstrap confidence intervals; if promising, condition insertion on board state or minion stats rather than universal rightmost.
- PR: https://github.com/sstxww/reinforcement-learning/pull/11 (draft). CI run 41413542460 succeeded on earlier head; re-check final head after this documentation commit.

## Pre-registered pilot versus fresh extension

- **Pilot** seeds 31001–31004 (observed before expansion): control mean 8.0000, candidate mean 6.2500, candidate-minus-control -1.7500. One seed with a seven-rank gain drove this result.
- **Unseen extension** seeds 31005–31020 (16 new paired seeds, no strategy changes): control mean 6.9375, candidate mean 7.2500, candidate-minus-control **+0.3125**. Positive means worse placement for the candidate.
- **All 20 pairs:** control mean 7.1500, candidate mean 7.0500, delta -0.1000. This near-zero aggregate does not support a robust performance improvement.
- Methodological lesson: never select a strategy from a four-game apparent breakthrough. Report fresh seed performance separately from the exploratory seed set. Do not merge this ablation into the shared baseline.
- First Action run failed from a mistaken test expectation (second hand's rightmost legal slot is action 61, not 55). The test was corrected in commit `d856106f338ee14e75c020cde9c7296b50035ae8`; later unit tests, TavernGym bootstrap, all full matches and receipt persistence passed.
