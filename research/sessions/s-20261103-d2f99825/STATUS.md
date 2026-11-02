# AutoTavern-AI V7: s-20261103-d2f99825

- **TASK_KEY:** `eval/per-seed-failure-provenance-v7`; **ROUND:** 001; **role:** REPAIRER/EVALUATOR; **state:** running, NOT integrated.
- **Base main SHA:** `3a745c6f6a48c65528bcbeb81b8627b8db93f046`; branch `agent/s-20261103-d2f99825/optimization-001`.
- Global atomic task claim: **not asserted**; this session owns only new `scripts/v7_seed_isolation_d2f99825.py`, `tests/test_v7_seed_isolation_d2f99825.py`, session docs, and own read-only workflow. No global integration lease was acquired. Do not merge on this session's authority.
- Existing main included merged #116/#117/#125/#154/#166/#176. Main CI must be rechecked on the latest exact SHA.
- Inherited PR #165: real 1408→1536 resumed PPO, a candidate-only complete rank-8 game on seed 932031, but held-out batch aborted with `Full-game safety limit exceeded`; the failing seed was **not logged**. Exact source https://github.com/sstxww/reinforcement-learning/pull/165 and https://github.com/sstxww/reinforcement-learning/actions/runs/41509707315.
- **Minimal independent fix:** fail-closed per-seed raw model/baseline runner; save individual complete-game receipts immediately; record each failure's exact seed/arm, without inventing placement; paired stats only from completed matched seeds. No shared evaluator/trainer/registry edits.
- **Synthetic regression:** eight local tests passed before push; these synthetic fixtures are NOT game evidence. New code requires its own actual GitHub CI and TavernGym match evidence.
- Official source checkpoint: `v5-s-20261102-68099929-1408-41428692617` (1408 steps, unpromoted), weight SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. This session did not download/resume it. Engine: TavernGym 1.1.0 / source hash `6d8712c93022ba11`, observe2 4017/447, 245 actions.
- **Own new PPO steps:** 0. **Own raw model games:** 0 so far. **Own model checkpoint/Release:** none. **Promotion:** none, Best/Champion remain null as of base-main registry.
- **Own planned real test:** pinned eight-seat **baseline-only** seed 99437 seat 0 vs 7 scripted bots, action receipts in isolated workflow Artifact. Do not call this model-strength evidence.
- **Live run/receipt/PR/head CI:** pending actual result; no success claimed in advance.
- **Open integration gate:** PR #165 still Draft / its exact-head checks and current-main compatibility need independent review; no uncontrolled main merging. This patch also needs original complete-game receipt committed, exact-head PR CI, and integrator's exclusive merge authority.
- **Failure/retry budget:** one Actions smoke, up to two meaningful fixes; avoid duplicate multi-hour PPO runs.
- **Next exact action:** inspect own workflow run triggered by the single workflow-file commit; verify job logs and download its original output, commit genuine receipt if completed, then create non-Draft PR and inspect latest-head CI.
