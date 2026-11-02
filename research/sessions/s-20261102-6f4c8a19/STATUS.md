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
