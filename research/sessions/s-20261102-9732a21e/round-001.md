# V5 integration and bounded restore study — s-20261102-9732a21e, round 001

## Scope and provenance
Session: `s-20261102-9732a21e`. Unique branch `agent/s-20261102-9732a21e/optimization-001`; initial main `3c65ffd0380d6269e6b39c7bf1ca2d84281546d8` after integrating PR #70. Sole writable repository: `sstxww/reinforcement-learning`. Upstream TavernGym is read-only; no official Arena games.

Read the V5 Gmail attachment in full and examined main, 68 open PRs at the initial inventory, latest Actions, six Releases, AGENTS.md, session protocol, and the current train/evaluate/model modules. Concurrent agent integration changed main during inspection, so results must always be linked to exact SHA.

## P0: completed real integration
Reviewed [#70](https://github.com/sstxww/reinforcement-learning/pull/70) exact head `d1b9e925f3a3defaf7df784c19b3d67360a40c25`, its add-only mechanics audit module/tests, pinned TavernGym 1.1.0 fingerprint `6d8712c93022ba11`, real completed eight-seat seat-0 baseline game seed 83171 (rank 8, 60 decisions, 0 illegal, 0 combat truncations), and exact-head independent [CI #41422507115](https://github.com/sstxww/reinforcement-learning/actions/runs/41422507115) success. Claimed integration in GitHub comment, marked PR ready, and performed SHA-guarded squash merge `3c65ffd0380d6269e6b39c7bf1ca2d84281546d8`. This is a rules-data correctness audit, **not** a model strength gain; no new Champion. Post-merge CI requires separate verification.

PR #25 strict receipt audit was merged by a concurrent integrator as `f29a0a6e99161aca4163e51427f6bfabbe02f76f` before this session attempted any merge. Do not merge it twice. PR #8 infrastructure/registry and #9 resumable PPO remain broad draft integrations at inventory, requiring an updated overlap/conflict/CI review. #75 overlaps public mechanics audit work and should be deduplicated, not blindly combined. The many standalone negative strategy experiments should preserve receipts without changing Champion.

## P1: recovery and storage verification (this branch)
A bounded branch-only workflow `.github/workflows/v5-resume-s-20261102-9732a21e.yml` is set to run on its source push: download existing *unpromoted* `v2-learning-41413557445` Release, hard-check expected weight SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a` and metadata SHA256 `6f0b433191a8242dcedc627f6be49d1551a82788ce7bfd8e60416ede8146acc0`, verify `engine` compatibility against pinned installed TavernGym, perform **128 continuation steps only**, demand candidate-only completed eight-player game and two new paired heldout seeds, then create a uniquely tagged unpromoted prerelease and **independently download/check bytes**. If any gate fails, it must not claim durable recovery or promote a model. Save real compact receipts, lineage and checkpoint SHA to session-owned paths; keep candidate weights out of Git history. Main shared train.yml is not modified and must not run on this branch.

This section describes the configured experiment, **not a claim of completed execution**. Record the actual GitHub workflow run ID, training steps, results, CI outcome and release URL only after GitHub confirms them.

## P2: evidence of persistent eighth place
The existing [PR #60](https://github.com/sstxww/reinforcement-learning/pull/60) reports *three actual heldout matches* for a lower-learning-rate PPO candidate: ranks [8,8,8], 36 actions including 21 model END_TURN selections, **zero buys** and zero forced fallback. Reference PPO: ranks [8,8,7], 875 actions, 20 buys, 21 guard forced ends. This is a concrete action-collapse lead, **not yet a causal diagnosis of low learning rate** or proof that a buy was legal in those states. Model confidence, legal-buy opportunity denominator, observation features, economy and reward/advantage distribution are required for falsifiable causal analysis. Other rule baselines themselves often place seventh/eighth; benchmark weakness and action collapse are distinct questions.

Do not infer that 128 more steps will improve rank. Only advance to larger-scale training if checkpoint restore, pure model game, legal action audit, and meaningful paired heldout behavior/uncertainty have passed.

## Current execution counters (at document creation)
- Direct PR #70 merges performed by this session: **1**.
- PR #25 merged by a different concurrent integrator: **1 observed**, not credited to this session.
- Verified new PPO steps from this session: **0 so far**, workflow configured but results pending.
- New completed candidate model games by this session: **0 so far**.
- New Champion promotions: **0**.
- Source official Arena games: **0**.
- Main CI final success for #70 integration: **pending verification**.

## Next acceptance gate
Read Actions status for exact workflow-source head and post-merge main; resolve real logs on failure (maximum two substantive fixes), inspect artifacts/Release hash roundtrip; update this session's evidence only. If candidate action/canary guard fails, record failure without counterfeit receipt, and prioritize a state-and-legal-mask telemetry experiment over larger PPO runs.
