# R002 — Real shop refresh before first purchase, activated but strength unproven

## Scope, identity and evidence sources
- Session: `s-20261102-6cc5d763`.
- Independent branch `agent/s-20261102-6cc5d763/optimization-002` based on explicit main SHA `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Draft [PR #33](https://github.com/sstxww/reinforcement-learning/pull/33), against main; merge requires current-head CI and human review.
- Previous own Round 001 [PR #27](https://github.com/sstxww/reinforcement-learning/pull/27): 7 real complete games but no activation. This distinct R002 hypothesis deliberately changes the trigger and uses separate source/workflow/seeds.
- Hypothesis: on turns >=4 when original baseline selects a legal Buy and Refresh is also legal, at most one refresh before buying per turn may improve rank.
- Upstream `actions.rs` confirms 0=EndTurn, 1=Refresh, 8..16=Buy; all actions remain masked.
- Source `tavern_ai/prebuy_refresh.py`, tests `tests/test_prebuy_refresh.py`, workflow `.github/workflows/experiment-s-20261102-6cc5d763-002.yml`. No changes to shared baseline, shared training, other sessions, upstream or Arena.

## Real execution
- Completed successful Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41415776708 (actual game+artifact job).
- TavernGym 1.1.0, verified source fingerprint `6d8712c93022ba11`, 4017 features / 447 card positions / 245 actions; seven native scripted bots.
- Candidate policy SHA256 `8af4b69abc82f6c7edc415352f23a73a7a502725cdaa1bbd7129b8b2527fd010`.
- PPO steps **0**; rule-tuning experiment only. No candidate model checkpoint, so Best and Latest model state unchanged.
- Initial code SHA `424edaa91f6a7b7257946dfcd2b82cfebf2267bc`. Genuine receipts/metric commit `af075f4419a73b5097bf1fba793a90c9a36c9e4a`.
- Successful environment installation, Python tests, code/contract, nine complete TavernGym eight-seat matches, receipt verification, git evidence commit and artifact preservation.
- Mandatory candidate-controlled seed **36511**: `Game.is_over()==True`, rank **8**, 43 decisions, 14 turns, 5 refresh actions, final eight seats `[8,6,3,4,2,7,1,5]`, truncated combats 0, turn-limit end false; receipt `experiments/s-20261102-6cc5d763/002-36511.json`.

## Paired independent evaluation
| Seed | Unmodified baseline rank | R002 candidate rank | Candidate - baseline |
|---|---:|---:|---:|
| 36512 | 5 | 7 | +2 (worse) |
| 36513 | 8 | 8 | 0 |
| 36514 | 7 | 2 | -5 (better) |
| 36515 | 8 | 8 | 0 |

- Baseline: n=4, mean rank **7.00**, first place 0/4, top 4 0/4.
- Candidate: n=4, mean rank **6.25**, first place 0/4, top 4 1/4 (25%).
- Mean paired candidate-minus-baseline rank delta **-0.75**. Paired deltas [2,0,-5,0].
- Candidate refresh counts for canary plus holdouts **[5,5,6,9,7]**, **32 actual interventions**. Experimental exposure gate passed. No invalid candidate actions or engine truncations.
- Main interpretation: a suggestive average-rank difference on four seeds, **not a robust competitive improvement**. One seed yields the entire apparent upside while seed 36512 is worse. Do not promote to Best.
- Exact metrics `reports/s-20261102-6cc5d763/round-002.json`. Original per-game JSON receipts `experiments/s-20261102-6cc5d763/002-36511.json` and `experiments/s-20261102-6cc5d763/r002-*.json`; native simulator completion proven independently via workflow.

## Prior learning, durability and next hypothesis
- Learned from R001's zero activation: make policy interventions observable and fail when no new action is taken.
- Learned from other session [PR #11](https://github.com/sstxww/reinforcement-learning/pull/11): a strong initial four-pair effect did not generalize across 16 additional paired seeds. Therefore extend heldout cohorts before claiming a real ranking gain.
- 30-day Artifact `prebuy-s-20261102-6cc5d763-41415776708`, ID `13127208879`, expires 2026-12-02 08:50:33 UTC. Only results/receipts are committed permanently; no model weights were created.
- Reproduction: install pinned TavernGym, run `python -m tavern_ai.prebuy_refresh --seed 36511 --start-seed 36512 --games 4`.
- No new runner or permission failure in Round 002. No temporary raw rollouts or model caches in git.
- Proposed next hypothesis: does this small pilot mean-rank advantage persist on >=16 fresh independent seeds? Use an isolated extension without modifying the original seven/nine match receipts.
- PR CI for latest research-summary commit remains to be checked, do not mistake the successful experimental run for the PR gate.
