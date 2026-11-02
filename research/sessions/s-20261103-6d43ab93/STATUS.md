# V7 STATUS — s-20261103-6d43ab93

- SESSION_ID: `s-20261103-6d43ab93`; ROUND: 001; Role: EVALUATOR/REVIEWER.
- TASK_KEY: `eval/1408-raw-seat1-seed99741`; atomic claim branch successfully created: `claims/eval-raw1408-seat1-99741`. This is a task claim, **not** an exclusive main-integration lease.
- Status: running; no claim of a completed Actions run or match until verified original evidence is added.
- BASE_MAIN_SHA: `990acd21d598a34a554a80c50089a8f1a9423ac4`.
- Branch: `agent/s-20261103-6d43ab93/optimization-001`. Current HEAD is the branch HEAD at time of inspection; follow GitHub history for precise current SHA.
- P0 review: #15 targets unmerged `agent/learning/v1` (#9 Draft); #174 and #168 are Ready independent main-based PRs; #172 and #179 also Ready, subject to fresh base/head/CI review. Already merged #117 (Release continuation), #125 (checkpoint stage), #176 (FREEZE provenance). **Merged by this session: none.**
- Latest registered source model: `v5-s-20261102-68099929-1408-41428692617`, Release https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617 ; SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; 1408 MaskablePPO steps. Engine TavernGym 1.1.0, source `6d8712c93022ba11`; observe2 4017 floats/447 cards/245 masked actions. Independent restore from this session: **not yet verified**.
- Budget: one fixed held-out seed 99741, controlled seat 1, scripted bots in other seats, two arms (baseline and raw PPO) if Release is restored, at most 6000 controlled decisions for each; no new training unless future budget/behavior gates warrant it.
- New training steps: **0**; new model/checkpoint/Release: **none**. No raw model match completion or improvement claimed yet. Prior main data for the registered 1408 model: heldout ranks [8,8,8], baseline [6,8,8], n=3, same seat=0.
- Own paths: `scripts/v7_seat_probe_6d43ab93.py`, `tests/test_v7_seat_probe_6d43ab93.py`, own workflow and session/report/proposal/receipt paths only.
- Own eight-seat original receipt: **pending verified workflow run**; never commit synthetic fixtures as evidence.
- CI: latest exact PR-head and main-head CI must be checked; no merge is approved solely by unit tests, and no global integration lock is held. On task exit report "handoff/finished" in this file; claim ref remains a historical ownership record.
- Blockers: local isolated container cannot resolve github.com and does not have TavernGym/sb3_contrib, so actual game must be performed by GitHub Actions; current connector has no Actions workflow_dispatch or Release-create function. Branch push is a real workflow trigger, but queued != completed.
- Next exact action: inspect `v7-seat-probe-s-20261103-6d43ab93` Actions run at workflow source HEAD, fetch job steps/logs and original artifacts, commit validated genuine baseline/model seat1 receipt(s) only if completed; write model failure JSON separately otherwise; recheck latest HEAD CI and Ready PR integration owner. No ranked TavernArena.
