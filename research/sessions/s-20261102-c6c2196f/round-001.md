# s-20261102-c6c2196f — Round 001, verified real-engine receipt integrity

## Hypothesis and rationale
Main's `tavern_ai.validate_receipt.validate` checks that eight placements lie between 1 and 8 but does not require a permutation, pinned source hash/version, valid integer seed, or a model hash when policy is a model. This can let malformed evidence into rankings/model-registry decisions. A separate strict validator can reject identifiable synthetic tampering while accepting real game receipts, without changing shared modules.

## Prior baseline / other agents
Based on main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d` (2026-11-02). Read README, AGENTS, docs/PROJECT_BACKGROUND, ARCHITECTURE, SESSION_PROTOCOL, CLOSED_LOOP, research/knowledge/README and INCIDENTS-20261102, current sessions/proposals, open PRs and Actions. Existing open PRs cover PPO and game strategy, evaluation, training recovery and infrastructure; isolated new files avoid overlap. A separate candidate of 1280 PPO steps has published a four-game all-rank-8 negative comparison (unmerged PR #15). That result is not our evidence.

## Actual code
- `tavern_ai/receipt_integrity.py`: fail-closed rank permutation, version/source fingerprint, seed, policy and SHA consistency, guard field types; delegates common checks to legacy validator without editing it.
- `tavern_ai/receipt_audit_experiment.py`: bounded real TavernGym three-game runner, original rule baseline on seat 0, synthetic tampering campaign against old/new validator; ensures strict game receipts written only after `Game.is_over()` via canary.
- `tests/test_receipt_integrity.py`: 12 tests including reproducible pre-existing duplicate-rank false acceptance.
- `.github/workflows/experiment-s-20261102-c6c2196f.yml`: branch-specific isolated workflow (65 minute bound, own concurrency group, only own receipts/reports committed). Evidence-only pushes exclude workflow source paths and do not retrigger experiment.

## Environment and execution evidence
- Engine: TavernGym 1.1.0, patched pinned upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, observe2 `4017/447/245`, source hash `6d8712c93022ba11`.
- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41414984419 — **success**; 12 targeted pytest cases passed, bootstrap verified engine, executed real games and validated all receipts.
- Source commit: `af50a0a18bc308d67099bd2992e6bd88ce7ecb4e`.
- Evidence commit: `5ccbd2b868b0194afc92dc76c0093418b43f5a15`.
- Training configuration: NONE, PPO steps: **0**, policy: **baseline** (not learned), model hash: null, no checkpoint or Artifact weights.
- CLI: `python -m tavern_ai.receipt_audit_experiment --agent-id s-20261102-c6c2196f --seed-start 36001 --games 3 --out-dir experiments/s-20261102-c6c2196f --report reports/s-20261102-c6c2196f/receipt-integrity.json`.

## Real independent eight-seat games

| Seed | Seat-0 rank | Decisions | Turns | Eight placements | Game finished | Combat truncations |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| 36001 | 8 | 47 | 14 | [8,4,7,1,6,2,5,3] | true | 0 |
| 36002 | 8 | 43 | 15 | [8,4,1,6,5,2,3,7] | true | 0 |
| 36003 | 7 | 52 | 18 | [7,3,2,6,4,5,1,8] | true | 0 |

All three reached `Game.is_over()`, `turn_limit_end=false`, real original TavernGym seat-zero baseline and seven official bots. Receipts: `experiments/s-20261102-c6c2196f/001-36001.json`, `001-36002.json`, `001-36003.json` (on own branch). Seeded mean rank **7.6667**, first-place rate **0% (0/3)**, top-four rate **0% (0/3)**. No gameplay improvement is implied; no candidate-vs-old policy experiment was conducted.

## Evidence audit results / interpretation
The following six synthetic corrupted variants of the first authentic receipt were deliberately **not** represented as actual game receipts: duplicate placements, wrong engine hash, wrong engine version, negative seed, model policy without model hash, unsupported policy name. Existing legacy validation accepted all six; new strict validation rejected all six. Measured synthetic mutation false acceptance: legacy 6/6 vs strict 0/6. This confirms a measurable validation improvement for precisely these cases. It does not establish comprehensive anti-tampering security, cryptographic signatures, or a competitive model.

## Problems and outcome
No fatal job failure in own action. Targeted unit test success and three real game completions are verified. The production validator is deliberately untouched to respect concurrent PR #8. Remaining review gate: CI on newest PR head, possible integration semantics and independent maintainer approval.

## GitHub evidence and next action
PR: https://github.com/sstxww/reinforcement-learning/pull/25 (draft, not merged). Report: `reports/s-20261102-c6c2196f/receipt-integrity.json`. No checkpoint was generated or saved; no persistent-recovery claim. No upstream or Arena write occurred.

Next hypothesis: quantify model-action no-progress cycles under a separately labelled model policy, rather than interpreting model rescue baselines as true model success. Do not start ranked Arena.
