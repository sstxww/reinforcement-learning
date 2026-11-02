# P0 Integration triage — concurrent GitHub snapshot, 2026-11-02 UTC

Session `s-20261102-7d32b871`. This is a **time-stamped snapshot**, NOT a standing automatic merge queue.

## Live snapshots and concurrent drift

- At initial inspection: main `db5e23ae8c218808821327d806b05d2604cfadfb`, **75 open PRs / 74 drafts**, latest main CI #41432038040 green.
- Later observed: main `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`, **99 open PRs / 98 drafts**. Main and open count changed during this session; re-query before any action.
- Only non-Draft PR observed was **#15**, base `agent/learning/v1`, not main; its parent **#9** remains Draft. A green stacked child is **not** authorization to merge into main.
- Concurrent integrator closed/merged former Draft #75 during our review; we did not attempt or take credit for that merge. Never merge a stale snapshot.

## Five V5 categories

| Category | Examples and latest observed condition | Required action |
|---|---|---|
| A. Can enter merge review | **No open PR independently certified by this session.** A green CI alone does not clear Draft/receipt/overlap review. | Maintain strict exact-HEAD, valid receipt and non-conflicting main compatibility review. |
| B. Repair before merge | #8 legacy infrastructure conflict; #94 and #105 reported non-mergeable; #95 and #86 became non-mergeable on latest snapshot. | Work only with owners or isolated compatible extraction; do not modify their branches or force merges. |
| C. Additional verification | #93 two-asset integrity checks draft despite earlier authentic match; #103 diagnostic draft; #9 V1 PPO draft. | Require latest-head PR CI, replay/receipt integrity, code diff and model/recovery gate where relevant. |
| D. Negative/inconclusive | #107 buy override: 46 buys in 3 true games but ranks [8,8,8]; #12 reward shaping 8704 PPO steps/46 matches with no gain; #15 V2 model no rank gain. | Preserve credible negative evidence, do not promote weak policy or pretend rule override was PPO learning. |
| E. Dependency/duplicate scope | #15 stacked on #9. #107 stacked on #103. #105 carried earlier #90 changes. #93 overlaps main's Release verification/integrity modules; compare helpers before extraction. | Resolve dependency ordering and de-duplicate on latest main; do not wholesale merge self-contained experiment stacks. |

## Relevant proven model-train blockers in main

1. `.github/workflows/train.yml` restores from prior success's temporary `v1-model` Actions Artifact. On missing/expired artifact the script discards the pair and silently starts from zero. This is **not** safe continuity from canonical Latest.
2. Main `models/registry.json` has 1408-step experimental Latest; `models/release_inventory_v5.json` intentionally maintains a separate discovery scope with null Latest, and `models/release_asset_digests.json` reports limited historical verification. An explicit per-run Release checksum + load + optimizer test is necessary before official continuation.
3. Own PR #113 is a read-only isolated preflight, **not** a finished shared train.yml correction. Pending CI / true receipt / safe merge review.

## Rank-8 provenance (no new assertions of performance)

- Genuine V2 action opportunity study #41428098018: n=2, 74 legal-BUY decision exposures, zero buys, 222/248 Refresh/Freeze, ranks 8/8.
- Independent raw model trace `reports/s-20261102-ba09e2d4/002-action-opportunities.json`: 2978 HeroPower and 2977 Cancel actions, incomplete at turn 3 after 6000 decisions; must not be counted as a full match.
- Genuine guarded study #41430849292: rank 8/8 with zero buys even under loop guard.
- 1408-step single-pair `reports/s-20261102-68099929/003-buy-opportunity.json`: raw model selected 0 buys across 35 mask-legal decision exposures and placed eighth; n=1 only.
- The corrective direction is state-change instrumentation, target-selection/Play↔Cancel semantics and ability to spend gold *without* overriding every legal BUY; better full-game ranks and no fallback remain a distinct gate.

## Integration decision

**No previous PR merged by this session.** No open PR met every safe merge gate in this fast-changing review. #113 remains Draft; its separate Actions job must finish and commit a genuine match receipt before being re-evaluated. Do not enter ranked TavernArena or overwrite another session's results.
