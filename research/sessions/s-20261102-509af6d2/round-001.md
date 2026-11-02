# s-20261102-509af6d2 — Round 001: Opening Tavern upgrade timing ablation

## Identity and hypothesis
- Session: `s-20261102-509af6d2`; isolated branch `agent/s-20261102-509af6d2/optimization-001`.
- Immutable main base: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d` (2026-11-02).
- Hypothesis: delaying the **turn-2** Tavern upgrade to **turn 3** might trade Tavern tempo for early minion purchases, improving placement versus `BaselinePolicy`.
- Source: `tavern_ai/s_20261102_509af6d2.py`; test: `tests/test_s_20261102_509af6d2.py`.
- Candidate policy SHA256, measured on the real runner: `7620db9bb2925336114ff133fd99af7e5f5afbc38b599006be2fb9ffa88ba692`.
- No production PPO, global strategy code, shared training workflow, upstream simulator or other session files modified.

## Why this direction
The main baseline hard-codes upgrades on turns `{2,5,7,9,11}`, and uses action 3 for upgrade. Open PRs were already exploring buy-slot tie-breaks, card embedding/pooling, PPO entropy, reward shaping and placement insertion, so this session selected a separate opening timing decision. Earlier public evaluation in `reports/evaluation/v1-baseline.json` found baseline ranks `[7,6,8,8]` in four *different* seeds; those are historical context **not** included in the paired results below.

## Engine, code and safety
- Real TavernGym **1.1.0**; pinned commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`.
- Public observe2 patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Verified engine source fingerprint `6d8712c93022ba11`, 4017 float features, 447 card ID slots, 245 legal-masked discrete actions.
- Candidate exclusively controls seat 0; the other seven seats use the real TavernGym `bot_play`. Every decision checks legal mask; each match checks `Game.is_over()==True`, placement permutation, no combat truncation, no forced turn-limit end and receipt schema.
- Candidate honors mandatory choices, play-first order, 85-action budget, and never masks away the only legal action.
- Pure **rules strategy experiment**; actual PPO gradient steps **0**. No checkpoint weights, optimizer, model hashes or training artifacts were created. `Latest`, `Candidate` and `Best` as PPO models: **not applicable**. Candidate is a versioned rule policy, unpromoted.

## Executed experiments and receipts
1. [Initial Actions 41415050033](https://github.com/sstxww/reinforcement-learning/actions/runs/41415050033): **success**, tests + engine verification + 4 paired seeds `38101..38104` = **8 complete matches**. Receipts `experiments/s-20261102-509af6d2/001-3810*.json` (candidate), `baseline-3810*.json` (control); comparison `reports/s-20261102-509af6d2/upgrade-timing-comparison.json`.
2. [Independent confirmation Actions 41415518707](https://github.com/sstxww/reinforcement-learning/actions/runs/41415518707): **success**, same unmodified candidate + fresh 16 seeds `38201..38216` = **32 complete matches**. Receipts `experiments/s-20261102-509af6d2/001-382*.json` and `baseline-382*.json`; comparison `reports/s-20261102-509af6d2/confirmation-16.json`.
3. Required own-model/strategy game: `experiments/s-20261102-509af6d2/001-38101.json`, seed 38101, candidate rank **8**, 47 decisions, 16 turns; full eight-seat placements `[8,3,6,5,7,4,1,2]`; `Game.is_over()` true; no truncation, no illegal action or turn-limit end. Actual run and originating SHA `e5818c6f0aa18191a5260a8a695948fd4ce659e7` recorded in receipt.
4. More favorable candidate case seed 38102: rank **1**, 112 decisions, placements `[1,5,8,3,2,4,7,6]`; this single first-place result must not be extrapolated.

| Dataset | N per arm | Baseline ranks | Candidate ranks | Baseline mean | Candidate mean |
| --- | ---: | --- | --- | ---: | ---: |
| Initial seeds 38101–38104 | 4 | 6,7,7,8 | 8,1,8,8 | 7.00 | 6.25 |
| Fresh seeds 38201–38216 | 16 | 8,8,8,8,8,7,4,8,8,8,6,8,8,7,8,8 | 8,8,8,8,7,8,8,8,7,8,7,8,1,8,3,6 | 7.50 | 6.9375 |
| Combined, all independent seeds | **20** | see above | see above | **7.40** | **6.80** |

- 40 full seeded matches, 20 distinct paired seeds, one controlled seat each.
- Baseline first-place 0/20 = 0%, top-four 1/20 = 5%.
- Candidate first-place 2/20 = 10%, top-four 3/20 = 15%.
- Candidate minus baseline paired mean rank **-0.60**, negative favors candidate.
- Paired differences are dominated by a few outliers; sample median difference **0**. Approximate two-sided 95% Student-t confidence interval for mean paired rank difference: **[-1.84, +0.64]**, includes zero.
- **Interpretation: not a verified strength gain.** The candidate may be promising but is volatile (numerous last-place finishes). This is not TavernArena Elo and not enough to promote a new `Best` policy. Do not merge as a competitive upgrade without further scrutiny.

## Failures, constraints and recoverability
- Both own Actions runs succeeded, so no own coding/engine/runtime failure to diagnose this round. No re-run or correction of the same failed SHA.
- Read examples from `research/knowledge/INCIDENTS-20261102.md`: model full-game safety limit, GitHub Release 403, position-encoding test mismatch, repeat Actions storms. Also independently inspected actual failed PR CI job logs where a PR lacked an independent receipt or supplied a non-complete receipt. Neither issue occurred in this session.
- No checkpoint to restore (rule-only). Git permanently retains compact source, JSON match receipts and analysis reports on this branch; the Actions evidence backup is **30-day retention**, not permanent model storage.
- Each workflow has a private concurrency group, fixed seed budget, 45-minute limit, paths-restricted push trigger. Receipt commit paths do not retrigger the experiment. No ranked TavernArena play.

## Reproducibility and next hypothesis
Initial:
```bash
python -m tavern_ai.s_20261102_509af6d2 --seeds 38101 38102 38103 38104 \
  --out-dir experiments/s-20261102-509af6d2 \
  --report reports/s-20261102-509af6d2/upgrade-timing-comparison.json
```
Confirmation: replace seeds with `38201..38216` and report path `reports/s-20261102-509af6d2/confirmation-16.json`, on pinned, hash-verified TavernGym 1.1.0 after `bash scripts/bootstrap_engine.sh`.

Next research hypothesis, **not yet tested**: consider a state-dependent opening upgrade delay rather than a fixed turn change, provided robust observation semantics are verified and the proposal avoids concurrent PR file ownership. Future integration must preserve baseline behavior unless independently proven better.
