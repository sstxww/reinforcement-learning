# Session s-20261103-dfaba893 — V7 R001

1. **TASK_KEY:** `review/pr175-rollback-toctou`; **role:** REVIEWER / RESEARCHER; **state:** running, integration blocked without globally enforced exclusive merge entry.
2. **Original BASE_MAIN_SHA:** `c1b828734527bae6141805581693d890cc3bff94`; last verified main at this SHA. **Own branch:** `agent/s-20261103-dfaba893/optimization-001`, current head must be fetched live.
3. **Inherited:** merged #117 Release restore, #125 staged write, #165 privilege-separated training, #176 raw model evidence. Reviewed open #175 Release restore and #185 pending serial integration workflow; merged PRs by this session: **0**.
4. **PR #175:** observed head `8f4be75cba8463a3f0a74f0e0b72a027a0bad8b5`; read-only CI #41511418837 SUCCESS, but current-main compatibility and TOCTOU rollback unresolved; Draft status fluctuates during concurrent author actions. Review comment: https://github.com/sstxww/reinforcement-learning/pull/175#issuecomment-6586804588. #185 actively updating/CI not yet accepted.
5. **Official model provenance inherited, not reverified here:** V5 1408-step unpromoted Release https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617 ; model SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; engine TavernGym 1.1.0, source hash `6d8712c93022ba11`, observe2 4017 floats/447 cards/245 masked actions. This session did not download weights or validate optimizer continuation.
6. **Training:** 0 new PPO steps; no training run, optimizer resume, or new Release by this session.
7. **Games:** no new verified own full eight-seat receipt at initial log time. A finite read-only branch workflow is configured separately; do not report gameplay until original Actions run and receipt are inspected.
8. **Paired comparison:** none; n=0 model games; improvement unknown, no model promotion.
9. **Confirmed behavior:** pure pathname `samefile()` + `unlink()` rollback is non-atomic; deterministic synthetic interleaving deletes a concurrently replaced file. **Not proved:** how often this happens in real GitHub runner checkpoint directories.
10. **Failure / reproduction:** `reports/s-20261103-dfaba893/rollback-toctou-reproducer.py` demonstrates identity-check/unlink race; standalone synthetic reproduction is NOT a production test or true game.
11. **Main integrated:** NO. Main CI SUCCESS: https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964 for `c1b828734527bae6141805581693d890cc3bff94`. Best/Champion untouched (no promotion).
12. **Next first action:** read PR #175 fresh head/diff and author's response to review; test failure scheduling *against the actual updated helper*, verify latest-head PR CI with a fresh current-main comparison, then route through an actually enforced exclusive integration entry. Do not direct-merge.

**Atomic task reservation:** `claims/v7/review-pr175-rollback-toctou` created successfully at original main SHA; this reservation covers the *review and reproducible counterexample only*. It does not grant a main merge lease or ownership of #175 production files. This session never held an exclusive merge lease.


## Concurrency deduplication / closure update

- **State changed to superseded / evidence-handoff-only** for the PR #175 rollback-race *review task*, not an integrated production fix.
- Current independently originated, more complete PR: [#188](https://github.com/sstxww/reinforcement-learning/pull/188), head observed `1636b98f6a0c3842788780074702c0fd8751c0b9`, non-Draft against `main@c1b828734527bae6141805581693d890cc3bff94`. It was opened before our branch and already contains deterministic rollback ownership tests, original run https://github.com/sstxww/reinforcement-learning/actions/runs/41512257198 and authentic **baseline-only** seed 99641 receipt; those are **not our session's game**.
- **No duplicate PR:** own evidence is kept in this branch and the issue #158 handoff; defer to PR #188 for integration review and to PR #175 author for production correction.
- The deterministic task claim `claims/v7/review-pr175-rollback-toctou` is no longer reserved for active work. A claim-status file is committed on the claim branch to explicitly record relinquishment; branch existence alone must not be treated as active ownership. This is **not** a main integration lease.
- Own read-only Actions run #41513610947 at source commit `285a1b68b340270d716036a025f287ea829f94e9` last returned **queued**, not a verified match; on later runs check the exact run and original artifact before recording rank or receipt. No training, model release or merge has been executed by this session.
- **Next first action for another session:** read #188 current head/CI, #175 patch and latest production review; avoid recreating this already demonstrated test. If #175 is corrected, run the post-positive-inode-check replacement regression against actual helper and check current-main synthesized merge/CI under a real exclusive integration mechanism.
