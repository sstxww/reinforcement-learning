# s-20261102-860ff0fd — R001 V5 P0/P1 integration and continuation gate

- Start main SHA: `db5e23ae8c218808821327d806b05d2604cfadfb` (CI success: Actions 41432038040).
- Open PRs inspected: 75 on 2026-11-02; 74 Draft. The sole ready PR #15 has base `agent/learning/v1`; parent #9 is Draft, so the dependency is not merge-cleared. A precise review hold was posted on #15.
- Existing main `.github/workflows/train.yml` restores an expiring `v1-model` Artifact and silently reinitializes if retrieval fails; it does not select a durable Release even though `models/registry.json` contains a verified experimental continuation source. This is the scope of this integration slice.
- Main registered `latest` is the UNPROMOTED V5 1408-step candidate Release `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Model game rank 8; paired heldout rank [8,8,8] versus baseline [6,8,8], no gain. `best/champion` remain null.
- New opt-in fail-closed selector cross-checks immutable tag, exact release, source digest, model metadata contract and canonical candidate, before model bytes are downloaded. Existing checkpoint preflight verifies actual Release bytes and ZIP+optimizer/engine, then performs one legal masked CPU inference step.
- Main training job is changed **in this PR only** to use this pinned Release, not silently start new random weights. Normal training `--resume` recovers the prior PPO model. Output still uses a 90-day Artifact: **automatic permanent save of the next training result is not solved by this slice**.
- V5 P2 evidence from separate PRs #103/#107 and integrated main: V2 PPO failed to choose BUY across many mask-legal opportunities, and adding forced BUY alone still produced three rank-8 outcomes while Play/Cancel loops persisted. This is a confirmed behavioral problem and not proof of one causal algorithmic defect.
- This session begins with **0 newly completed PPO steps** and **0 independently completed own games**; the branch-specific bounded Actions workflow attempts a real Release restore, a 128-step continuation, a model-controlled full game and a baseline game. Update verified outcome strictly from the real run; failed runs do not count.
- No Champion promotion, official Arena match, main direct push, or other agent branch mutation.
- Integration rule: keep PR Draft until exact final-head CI, own authentic eight-seat receipt, run logs and restoration gates reviewed. If main advances under another agent, recheck before merging.

## Recommended next integration

1. Verify actual smoke workflow run, source weight SHA and optimizer step increments; classify raw versus guarded model game.
2. Validate own receipt and exact PR CI; leave Draft if unresolved.
3. On success merge only after latest main conflict review and inspect post-merge main CI.
4. Follow with durable *output* release publication and version-index PR; current job's upload-artifact cannot be a lasting resume chain.
