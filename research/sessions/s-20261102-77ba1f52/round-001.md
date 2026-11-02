# s-20261102-77ba1f52 R001 — P0 integration guard and canonical Release consistency

## State at start
- Isolated branch: `agent/s-20261102-77ba1f52/optimization-001` from main `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
- Initial inspection: 75 open PRs, overwhelmingly Draft; #15 depends on Draft #9 and targets `agent/learning/v1`. Main advanced concurrently; snapshot requires refresh.
- Existing canonical `models/registry.json` has 5 unpromoted candidates; `models/release_asset_digests.json` has 7 Release records; legacy `models/release_inventory_v5.json` has 6. These scopes are not interchangeable.
- PR #93 final-head 650f6285 has successful historical CI but its test hardcodes exactly 4 canonical candidates. A factual merge blocker comment was posted: https://github.com/sstxww/reinforcement-learning/pull/93#issuecomment-6577831058. This is a predicted post-merge incompatibility, not a claimed actual merge failure.

## This integration slice
New, session-only `tavern_ai/release_consistency_77ba1f52.py` and offline regression tests reconcile the **single canonical** registry against release-asset digest claims and the separate legacy inventory. They fail closed on missing latest digest, mismatched SHA, invalid URLs and duplicates; they deliberately do not require legacy inventory and canonical list sizes to match.
The output distinguishes metadata-index consistency from actual weight bytes, model load, optimizer resume, model-only complete match, and competitive improvement. It is **not** a second model registry and never promotes a Champion.

## Performance evidence and gate
Canonical latest unpromoted V5: 1408 steps, heldout ranks [8,8,8] vs baseline [6,8,8]. No claim of a stronger model. Other V2 evidence includes zero buys despite legal opportunities; PR #107's forced-BUY ablation still reports last place, so single-action fixes are insufficient. Hypotheses need independently instrumented tests.
No new PPO training has been started by this slice. No official Arena play.
A session-only GitHub workflow is to execute offline tests, install pinned TavernGym and create an **original baseline 8-seat game** on its own branch. Until its completed run and committed receipt are verified, this PR remains Draft. A baseline match is engineering evidence, not model-strength evidence.
