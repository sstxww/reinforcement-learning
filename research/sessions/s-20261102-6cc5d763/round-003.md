# R003 — Independent 16-pair extension of unchanged R002 refresh policy

## Identity, hypothesis, study design
- Session: `s-20261102-6cc5d763`, isolated branch `agent/s-20261102-6cc5d763/optimization-003`, main base commit `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- [Draft PR #42](https://github.com/sstxww/reinforcement-learning/pull/42), unmerged and dependent on careful comparison with the identical source in [R002 PR #33](https://github.com/sstxww/reinforcement-learning/pull/33).
- Hypothesis: the provisional R002 mean-rank gain (-0.75 over 4 pairs) persists on 16 untouched seeds, without any model or policy parameter change.
- Frozen source: `tavern_ai/prebuy_refresh.py` copied bit-for-bit from R002; enforced SHA256 `8af4b69abc82f6c7edc415352f23a73a7a502725cdaa1bbd7129b8b2527fd010`, verified **before** full games.
- New files: `tavern_ai/prebuy_extension.py`, targeted tests, dedicated 80-minute branch-only Actions workflow. No shared baseline/PPO/other session changes.

## Actual complete-game run
- Successful dedicated Actions: https://github.com/sstxww/reinforcement-learning/actions/runs/41416484290; job real engine, tests, 33 completed games, receipt validation and own-branch evidence commit all succeeded.
- Engine: TavernGym **1.1.0** from pinned upstream patch, source hash **`6d8712c93022ba11`**, observe2 4017 features/447 card slots/245 legal actions.
- One candidate-controlled seat versus seven native script bots in each game; all actions verified against native legal-action mask.
- Own mandatory seed **36520**: `Game.is_over()==True`, seat0 rank **7**, 79 decisions, 15 turns, 7 refreshes, placements `[7,4,6,1,3,8,5,2]`; combat truncations 0, turn guard false; receipt `experiments/s-20261102-6cc5d763/003-36520.json`.
- Heldout seeds **36521 through 36536**, sixteen unchanged-baseline games and sixteen frozen-candidate games. Every one reached true game over, with no engine safety termination.
- Session original R001: 7 genuine full games (zero refresh activation).
- Session R002: 9 genuine full games (32 refresh activations).
- Session R003: **33 genuine full games** (93 refresh activations across 17 candidate games).
- Cumulative this session: **49 complete actual TavernGym eight-seat games**. No Arena games.

## Independent R003 evaluation result
- Baseline ranks: `[7,8,7,8,8,8,8,7,7,8,7,8,7,7,7,8]`, mean **7.50**, first place 0/16, top4 0/16.
- Candidate ranks: `[6,8,8,8,8,5,8,7,4,7,8,8,7,8,8,8]`, mean **7.25**, first place 0/16, top4 **1/16 (6.25%)**.
- Paired candidate-minus-baseline ranks: `[-1,0,1,0,0,-3,0,0,-3,-1,1,0,0,1,1,0]`, mean **-0.25** (negative is better).
- Pair difference sample SD **1.2383**. 10,000-resample paired bootstrap 95% percentile interval **[-0.875, 0.3125]**, deterministic bootstrap seed **20261102**.
- The interval crosses zero: **no reliable improvement demonstrated**. This is a descriptive simulation estimate, not Arena Elo or a statistically compelling performance gain.
- R002 + R003 total 20 independent heldout seed pairs (disjoint): baseline mean rank **7.40**, candidate **7.05**, delta **-0.35**. R002's four-pair apparent gain shrank in the fresh 16-pair cohort.
- Candidate actually made **93 refreshes** over the R003 canary and 16 held-out games; unlike R001 there is positive intervention evidence, so this is a meaningful gameplay comparison.

## Training, checkpoint custody, failures and lessons
- RL training steps **0**; R003 is a rule-strategy evaluation, not PPO training. No weights/checkpoint, neither Latest nor Best modified/promoted.
- Initial R003 code SHA `08f5c1b41ef8a8636a02949d32f426ff52e793ec`; real metrics/receipts commit `15ccfff2df0a6f7db4a2b1843d0d62871c1a2eb9`.
- Fine-grained report `reports/s-20261102-6cc5d763/round-003.json`; candidate/unchanged baseline receipts `experiments/s-20261102-6cc5d763/r003-*.json`.
- Evidence-only Actions Artifact `frozen-prebuy-s-20261102-6cc5d763-41416484290`, ID `13128475363`, expires **2026-12-02 08:56:53 UTC**. Small compact result JSON and all required receipts committed to Git; no model was produced or claimed permanent.
- Reproduce: install pinned engine, `python -m tavern_ai.prebuy_extension --mandatory-seed 36520 --start-seed 36521 --games 16` in an isolated cloud/Actions worker.
- No runtime failure, model-loading issue or 403 incident encountered in R003. No unauthorized permissions used. All results are unpromoted candidates.
- Lesson from R001: design interventions that actually fire; from R002 and other session PR #11: a four-pair pilot is insufficient, extend to untouched seeds. R003 confirms a smaller descriptive delta on new seeds with uncertainty that includes no effect.
- Next practical research hypothesis: improve *card/board-aware shop decision quality* rather than unconditional reroll timing, since both current arms remain near 7–8th place. Requires its own independent code/holdouts and should not mutate these frozen receipts.
- PR latest-head independent CI must pass after this research-note commit; no merge without reviewer.
