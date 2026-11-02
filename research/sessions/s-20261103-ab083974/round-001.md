# V7 Round 001 — P0 restore rollback ownership review

SESSION_ID: `s-20261103-ab083974` | TASK_KEY: `review/pr-175-rollback-race` | Role: REVIEWER
Claim branch: `claims/v7/review-pr175-rollback-race` created atomically. This grants no main integration authority.
Original examined main commit (moving concurrently): `3a745c6f6a48c65528bcbeb81b8627b8db93f046`.
Own branch: `agent/s-20261103-ab083974/optimization-001`. Existing PR #175 target main, exact reviewed head `979932f36928dfbd30fd4109a29841178e3c19a1`.

## Inherited and triaged
- Read V7 32,014-byte Gmail TXT in full, latest main training workflow, AGENTS and coordination rules, canonical restore, trainer and evaluator, registered 1408-step checkpoint and Release provenance.
- Other agents integrated prior Release resume and checkpoint writer work. Do not reset training to Artifact-only.
- #15 is non-Draft but stacked on `agent/learning/v1` and Draft #9; not independently mergeable to main.
- PR #175 already owns `tavern_ai/release_restore_entry.py`; this session deliberately does **not** modify that shared production file or another owner's branch.

## Independently reproduced high-priority defect
PR #175's rollback uses non-atomic `destination.samefile(source)` followed by `destination.unlink()`. A concurrent new owner can replace the pathname in between. Local fault injection in a clean Python temporary directory produced `race_triggered=True third_party_file_survived=False source_bytes_untouched=True`. This was **a synthetic reproduction**, not real gameplay. Source PR regression races before the check, not this window.

The GitHub API rejected formal `REQUEST_CHANGES` with 422 because all PRs belong to the same linked GitHub account; a detailed **PR Conversation comment** was posted at https://github.com/sstxww/reinforcement-learning/pull/175#issuecomment-6586652843. No approval or merge occurred.

## Code contribution
New session-unique `tests/test_v7_restore_rollback_race_ab083974.py` includes a reproducing negative control, a safe no-rollback control, and a conditional future-installation gate. The final test **skips while main lacks the pending helper** and activates when merged. This test does not itself repair the unsafe production helper.

## Runtime and training evidence
- Own PPO additional steps: **0**. No own model weights, optimizer checkpoints, Release or Best promotion.
- Reused indexed historical **unpromoted** 1408-step source: `v5-s-20261102-68099929-1408-41428692617`, ZIP SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Neither re-downloaded nor independently optimizer-resumed in this review.
- Existing registry reports prior held-out PPO ranks [8,8,8] vs baseline [6,8,8], n=3; does **not** establish cause. Candidate unchanged; Best/Champion remain null at review.
- TavernGym interface in main: 1.1.0, engine hash `6d8712c93022ba11`, observe2 4017 features / 447 cards / 245 legal-masked actions.
- Unique read-only workflow is intended to run local tests and one real eight-seat **baseline only** seed 99641; at documentation creation not yet asserted to have executed or completed.
- No model-vs-baseline evaluation, raw policy improvement, or official ranked Arena action.

## Integration and handoff
Do not merge PR #175 as-is, nor mark it ready based only on previous source CI. Owner/integrator should patch check-then-unlink race, add post-check adversarial regression, verify exact-head CI/true receipt/current-main compatibility, and only then evaluate eligibility under a real exclusive main merge lease. Never treat this claim branch as merge authority.

Next operation: verify this session's one-shot Actions job and genuine baseline receipt; inspect final PR head CI; record actual receipt/PR URL; relay the PR #175 blocker to the integrator.
