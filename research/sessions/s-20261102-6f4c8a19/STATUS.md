# Session status — s-20261102-6f4c8a19

- Phase: P1 release recovery/verification experiment on isolated branch.
- Initial main: `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`.
- Historical candidate: `ppo-v2-1280-41413557445`, not Champion.
- Status: **verification pending Actions run**. No independent restore or training results can be claimed yet.
- Recorded prior PR #15 heldout rank-8 pathology; need legal BUY opportunity, raw action and gold/board trace before claiming causal cause.
- Workflow: `.github/workflows/recovery-s-20261102-6f4c8a19.yml`.
- Generated evidence locations (only if run succeeds): `experiments/s-20261102-6f4c8a19/`, `reports/s-20261102-6f4c8a19/`, and immutable experimental prerelease.
- No direct main writes, no upstream changes, no ranked TavernArena.

## Verified failure and R001 repair
- Own full cloud run [#41427594361](https://github.com/sstxww/reinforcement-learning/actions/runs/41427594361) installed dependencies, passed unit tests and installed pinned engine, downloaded real V2 Release, then stopped at schema-1-only validator (traceback: `Incompatible checkpoint metadata schema/algorithm`). Zero new PPO steps or full model matches.
- Independently downloaded that run's 17,525,115-byte model archive and 932-byte metadata via Actions artifact; model SHA256 equals trusted historical V2 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. Metadata is legitimate `schema:2`, model-compatible and contains full fingerprints. This is a checkpoint auditor schema mismatch, not a proved damaged ZIP.
- Repair attempt 1: support schema 2 with strictly enforced embedded digest, vocabulary 3984, catalog/ruleset/patch/upstream fingerprint. Four extra regression tests added. Do not claim success pending next actual run.

## R001 verified result (genuine GitHub run)

- [Actions #41428503929](https://github.com/sstxww/reinforcement-learning/actions/runs/41428503929) on input commit `2811ed957f14e4013d087f2684af0385763eaba4`: **SUCCESS**, actual pinned engine installed; all regression tests, V2 Release SHA + schema2 fingerprints, CPU loaded PPO and nonempty optimizer state, 128 genuine resumed PPO steps, full model-controlled game, paired evaluation, actual evidence commit and versioned experimental Release completed.
- Source weights: V2 Release 1,280 steps, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. Verified `load_and_optimizer_verified` in `reports/s-20261102-6f4c8a19/001-restore-audit.json`.
- Resumed **1,408 cumulative steps**, new SHA256 `7703791fe1d7de3951023cdcb9096ee0f8b3808f897cc320a34c15a6627f3401`, Release [v5-s-20261102-6f4c8a19-41428503929](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-6f4c8a19-41428503929). GitHub Release published with 5 supporting assets; this session has not independently re-downloaded the new Release and cannot claim a round-trip restore of these new bytes.
- Real pinned TavernGym full eight-seat model-controlled game seed 68112: **rank 8**, 123 decisions, 14 turns, `completed=true`, no combat truncation, no turn-limit ending, 245 legal-action mask. Mandatory separate baseline seed 68111: rank 8, 57 decisions, 17 turns. Receipts persisted in `experiments/s-20261102-6f4c8a19`.
- New fixed paired heldout seeds 68121/68122: candidate ranks [8,8], baseline ranks [8,8], both mean 8, top4=0%, first=0%, candidate-baseline delta=0. **No measured competitive gain**; comparison is candidate vs baseline, NOT new-vs-old PPO causal attribution.
- Never promote as Champion. Next mechanism-specific P2 step should count legally affordable BUY opportunities and END_TURN-with-BUY opportunities, instead of blindly scaling PPO. Cross-reviewed with existing draft PR #98; avoid duplicating its telemetry code.
- Guard against automatically retriggering training after bot receipt commits: change `recovery-s-20261102-6f4c8a19.yml` trigger to only code/tests/workflow/registry paths (commit `b1be4a98353c9732db4ca4b319b8565bbe2458de`). One redundant workflow push was queued when that trigger changed; session will not label it as a distinct verified improvement.
- PR #82 remains **Draft**, pending latest-head independent full-match CI and integration review. No direct main edits, no ranked Arena.
