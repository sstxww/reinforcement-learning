# V5 R001 — PR integration inventory and Release-backed model integrity scaffold

Session: s-20261102-6b4eaf12
Base main SHA: f29a0a6e99161aca4163e51427f6bfabbe02f76f
Repo: sstxww/reinforcement-learning (only write target).
TavernGym contract: 1.1.0, source_hash 6d8712c93022ba11, 4017 float / 447 cards / 245 mask actions.
Scope: new model registry + tests + isolated true-match workflow. No model policy/trainer changes.

## P0 review snapshot (2026-11-02 UTC)
- GitHub API returned 68 open PRs. Most are Draft and explicitly warn against promotion; review exact live head before integrating.
- PR #15 is non-draft but targets agent/learning/v1 and depends on still-Draft #9; do NOT merge in reverse order.
- PR #43 is non-draft but currently unmergeable and overlaps with already-merged seat evaluation PR #47. Deduplicate rather than force merge.
- PR #25 is a useful isolated strict receipt audit but still Draft, requiring latest-head CI and production validator integration review.
- PR #60 includes a concrete held-out low-LR PPO behavioral warning: 3/3 rank 8, 0 BUY in 36 actions, versus reference 20 BUY in 875 actions (three matches). Legal BUY opportunity counts were not established; do not label "buy collapse" as causal proof.
- Other Draft negative strategy PRs (including #71,#74,#76,#77) must not be promoted purely to reduce backlog.
- No other session's branch or shared module was changed, no PR merged here before its draft/dependency gates.

## P1
Six non-draft/experimental GitHub Releases were visible via API. The v1 and v2 Releases have model.zip and model.metadata.json plus GitHub-provided SHA256 digests.
V1 #9 reports 256 PPO steps and V2 #15 reports 1280 cumulative PPO steps, both poor full-game performance.
Added models/registry.json with two *unverified* identifiers and explicit Champion=null; model_registry.py performs offline SHA256 + archive CRC + model/optimizer member + engine-shape preflight; tests reject tampered digest, incompatible observations and nonexistent champion.
No model was downloaded or deserialized for this run, so model load, continued training, and full-game proof remain unverified. Weights were not modified or republished.

## P2
The 8th-place pattern is demonstrable from existing PR records but not yet causally isolated. The strongest actionable hypothesis is phase/action-family collapse and/or economic opportunity miss.
Need opportunity-conditioned counts: when BUY legal, how often BUY chosen; when PLAY legal, played; unused gold and board size by turn; model-selected END_TURN vs forced end; stage-specific divergence; compare on seat-rotated paired seeds.
Do not train more PPO until telemetry plus reliable release restore gate is available.

## Executed / planned verification boundary
Code and tests committed on this branch, unit/independent full-game CI is triggered by branch-specific workflow. Treat results as pending until confirmed in live Actions, then update report.
PPO steps newly trained: 0.
New model weights/checkpoints: none.
Arena ranked games: 0.
Do not invent match placement, receipt, CI success or Champion.

## Next integration work
1. Validate this branch's latest workflow and the independent PR CI, including its real-game receipt.
2. Test actual V2 Release download hash and trusted load+resume (avoid silent fresh start).
3. Extract opportunity-conditioned action telemetry from #60 without adopting unproven policy changes.
4. Once gates pass, integrate the small registry through reviewed PR and verify main CI success.
