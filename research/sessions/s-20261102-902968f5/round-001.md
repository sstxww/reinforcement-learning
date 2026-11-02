# s-20261102-902968f5 — Round 001: V5 release lineage and integration

## P0 inventory and non-overlap
Read latest V5 Gmail TXT (27,248 bytes), repository README/AGENTS/protocol, source trainer, canary, evaluator, main workflows and selected open PRs. At initial inventory 68 open PR, six GitHub Releases, main `0cd377e` with successful CI. Main advanced to `42f4cf3` while other sessions safely merged #26/#47/#43/#25/#37; do not claim those merges as own work. Draft PR #8 proposes model registry but conflicts with main; PR #9 provides schema-2 integrity logic; dependent PR #15 trains V2. The new change reuses schema-2 format and trusted Release asset digests without modifying the shared training or storage files touched by these PRs.

## Evidence and hypotheses
- Current production `train.yml` picks a 90-day Action artifact and has no persistent-Release restore fallback.
- Six actual Releases exist (API checked). V2 tag `v2-learning-41413557445`, source commit `e37bd7e3a4bf95576ca1b27867df05af86ddab71`, 17,525,115-byte model asset with GitHub reported digest `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. Companion digest `6f0b433191a8242dcedc627f6be49d1551a82788ce7bfd8e60416ede8146acc0`.
- PR #15 reports real 1,280-step MaskablePPO checkpoint and paired 4-game [8,8,8,8] ranks for both V1 and V2. No confirmed improvement, Best null. PR #60 reports a low-LR PPO model selecting 0 buys in 3 heldout full matches, while a reference made 20 buys and had repeated action-loop guards. This is an observed model-specific pathology; legal BUY opportunities remain unquantified, so causal explanation not established.
- P2 conclusion: ranking eighth cannot be attributed to training length alone. First priority after validated restore is action opportunity + board/economy telemetry; no blind large PPO.

## Code and bounded experiment
New pure-metadata `verify_source()` checks exact Release asset checksums, schema 2, algorithm, cumulative steps, 4017/447/245 native compatibility, card catalog, patch, ruleset and upstream commit. `audit_resume()` loads the model with native TavernEnv and policy optimizer, verifies legal action prediction, performs exactly a 128-step requested PPO continuation and writes new SHA256 plus exact step delta (no promotion). Workflow downloads source Release, runs new unit tests, completes original-Baseline canary, attempts resumed-model full game, and uploads a 30-day **diagnostic** artifact only. It can commit only own-session receipts and summary, never mutable source code or another session's files.

## Pending gates
Original source candidate has historical completed game and heldout evaluation; this session's training steps = 0 and full games = 0 **until the Actions workflow actually runs**. No new checkpoint was produced by this text commit. No claim of verified V2 Release resume until the live checksum/load/optimizer gate passes; no checkpoint is Champion. Need inspect latest PR/head CI, actual workflow logs and any real receipts before integration.

## Next actions
1. Trigger branch workflow by code push, inspect result and real generated receipts.
2. If true 128-step resume and model full game succeed, save verified report, open integration PR and review main compatibility; if failure, preserve failed status, do not invent results.
3. Follow up with main trainer Release fallback as a **separate reviewed** integration change after resolving #8/#9 overlap, then proceed to P2 model-choice/BUY-opportunity telemetry and independent paired evaluation.
