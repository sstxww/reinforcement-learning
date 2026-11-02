# s-20261103-b642f1d8 — V5 P1 integrity status

- Scope: an isolated, fail-closed regression fix on existing canonical `tavern_ai/train.py`, rather than a second trainer or model registry.
- Branch: `agent/s-20261103-b642f1d8/optimization-001` from `c8b46a64628b2540c7b6d9f3fdc1458bfe9207c3`.
- Changed: direct resume with SHA-less legacy sidecar is now rejected before loading; existing SHA-bound restore works as before; no change to saved model bytes or algorithm.
- Tests: targeted offline synthetic tests, not a simulator or real PPO-training proof.
- One-shot real eight-seat canary workflow will be independently inspected, and any bot-created receipt validated before merge. CI status not preclaimed.
- Known P0 blockers: Draft/stacked PRs, overlapping Release and shared-train changes, concurrent main movement.
- Known P1 blocker: main `train.yml` artifact-expiry fallback to random initialization; this branch does not claim that issue fixed.
- Known P2 failure: raw PPO tends to choose REFRESH/FREEZE with no BUY in legal-BUY states, plus separate HERO_POWER/CANCEL and PLAY/CANCEL loops. Not proven solved.
- Training/weights: 0 new PPO steps, 0 new releases, 0 Champion, 0 formal Arena games. No claims of successful candidate games until original receipts exist.


## Verified post-execution evidence (GitHub source of truth)

- Independent one-shot Actions run **41508443101 SUCCESS**, branch workflow head `cdea0ced077ec872430bbe7ead953988420dd907`. The targeted regression, TavernGym pinned install, real eight-seat baseline, receipt validation, branch receipt push, Release SHA audit and raw model probe all succeeded.
- Exact original own receipt: `experiments/s-20261103-b642f1d8/001-99383.json`. Baseline seed **99383**, game completed, 16 turns, 48 decisions, controlled seat 0 placement **7**, engine hash `6d8712c93022ba11`, no truncated combat or turn cap.
- Separate raw unguarded V5 1408-step PPO diagnostic seed **99384**, completed eight-seat game, placement **8**, 111 own decisions, 28 REFRESH, 70 FREEZE, 0 BUY across 27 temporally correlated legal-BUY decisions, 0 forced ends, 0 fallback. Published model SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Derived report `reports/s-20261103-b642f1d8/001-raw-model-diagnostic-99384-verified-summary.json` parsed from the authentic Actions stdout; original zipped evidence [Artifact #13172521754](https://github.com/sstxww/reinforcement-learning/actions/runs/41508443101/artifacts/13172521754), 30-day retention.
- Important: baseline 99383 and model 99384 are *different* seeds; no matched improvement effect. A model_gate completed-game diagnostic is not impersonated as a separate signed canary receipt. This proves persistent rank-eight/no-BUY behavior, not its exact root cause.
- Existing main integration by **other** sessions: #117 unified manual, durable Release-backed PPO restore, paired evaluation, and unpromoted Release save; #138 added strict Champion evidence gate. Neither is authored/merged by this session.
- The session's one-shot write-permission workflow was **deleted** from the final PR diff after real execution, preserving immutable Actions provenance without permanently adding dead privileged workflow code.
- Synthetic compatibility fixture for pre-existing test `test_refuse_wrong_step_count_after_load` corrected to have valid SHA (commit `19ef9b13f846cbe5d6febfe0298db3d704b5af76`). Subsequent full pytest: **335 passed, 1 skipped**; pre-receipt CI failed only because real own receipt was not yet committed.
- Own new PPO steps: **0**. Own new model Release: **none**. Best/Champion: **not promoted**. Formal ranked Arena games: **0**.
- Merge remains conditional on **latest exact-head CI completed/success**, current main compatibility, and postmerge main CI verification. No premature merge.
