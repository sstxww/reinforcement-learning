# V5 round 001: P0 integration audit, P1 paired evidence, P2 rank-eight diagnosis

SESSION_ID: s-20261102-c647a479
Starting main: db5e23ae8c218808821327d806b05d2604cfadfb
Own branch: agent/s-20261102-c647a479/optimization-001
Source: latest Gmail V5 TXT; 953 lines, 27,248 bytes read completely.

## P0 inventory and merge gate
- At inspection, 75 PRs open. 74 Draft; sole non-Draft PR #15 explicitly depends on still-Draft #9. No PR eligible for safe independent merge just to lower the count.
- Main HEAD db5e23ae8c218808821327d806b05d2604cfadfb passed push CI #41432038040. #108 integrated opt-in HeroPower-Cancel guard but two guarded games were both eighth place.
- Draft #83 duplicates registry-manifest coverage vs already-merged canonical registry, exact HEAD CI still required. Draft #86 continues isolated resume experiments. #103/#107 are stacked and overlap already-merged diagnostics. Do not override authors or merge without concurrency ownership.
- GitHub API returned 15 Releases, no declared Champion. Main train.yml still restores 90-day Actions Artifact, not a verified durable Release.
- Own main merges: zero. No official Arena, no upstream or shared main changes.

## P1 implementation
- Added standalone tavern_ai/paired_evidence.py with CLI and tests/test_paired_evidence_c647a479.py.
- Strictly validates genuine eight-seat receipt completion, full placement permutation, pinned environment, unique and paired seed/seat, one model SHA claim, bounded guard intervention counters and separate raw vs guarded model arms.
- Produces paired rank delta, win/top-four proportions and Wilson95 intervals; cannot prove model ZIP validity or causality.
- Local synthetic regression: 13 passed. Exact GitHub PR head CI and own authentic baseline canary still required before merge.
- Existing common train/evaluate/registry/workflow files untouched to avoid conflicting concurrent development.

## P2 evidence grounded in existing genuine runs
- Main report reports/s-20261102-83d91476/001-buy-opportunity-report.json: V2 on seeds 45111/45112 rank [8,8], 74 decisions with mask-legal Buy yet 0 buys; 222 of 248 raw actions are IDs 1 or 2. Baseline ranks [6,7], buys 33. Workflow 41428098018.
- PR #105 confirms from pinned source 1=Refresh, 2=Freeze, 8..15=Buy. Dominant action families established; rank causality and state change are not.
- PR #107 ran nine complete games on seeds 89111-89113. Legal-buy override produced 46 buys in three hybrid games yet every rank remained 8, with Play/Cancel looping and more guard-forced ends. Not unmodified PPO and not a remedy by itself.
- #108 HeroPower-Cancel guard lets guarded games finish, but both remained eighth; it does not establish neural policy learning.
- Next falsifiable test: log public-state deltas, gold/board/hand, legal-purchase opportunities and model logits by action family, then compare one isolated change on fresh paired seeds. No large PPO expansion while these deficits remain.

## Safety / limits
Training steps this session 0; new weight files none; own model checkpoint load 0; model-controlled games 0; no verified strength gain. Branch-scoped workflow is the only planned source of our own full-game evidence. If it fails or is blocked, leave Draft with the blocker.
