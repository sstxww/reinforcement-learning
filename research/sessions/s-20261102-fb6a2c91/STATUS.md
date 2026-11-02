# AutoTavern V5 — s-20261102-fb6a2c91 STATUS (R001 completed, integration Draft)

Own branch: `agent/s-20261102-fb6a2c91/optimization-001`. PR https://github.com/sstxww/reinforcement-learning/pull/133. Original main base: `ef77ae6bc5d9bef09e903fac7705917ec3b7366d`; main is moving concurrently. Upstream read-only. Only own isolated branch modified. **No Champion promotion or main merge.**

## P0 direct integration audit
- Commented on #93 blocking a merge: its tests hard-code 4 candidates and full metadata index coverage, but canonical main already contains 5 (including V5 1408) and has an existing dual-asset verifier. Prior green head-CI does not prove merge compatibility. Do not merge unchanged.
- Commented on #15: only ready-to-review PR depends on still Draft #9; V2 continuation showed no gain. Hold stacked merge.
- Reviewed rank-eight evidence and posted pinned-engine semantics to issue #78. No PR in that pair safely merged by this session.

## P1 real Release-backed resume and archive — VERIFIED
- Actual independent GitHub Actions run https://github.com/sstxww/reinforcement-learning/actions/runs/41450269678: **SUCCESS** including tests, pinned engine, original full game, parent Release download, hash/CPU-load gate, true MaskablePPO incremental training, model-only canary, two-game paired heldout evaluation and GitHub Release publication.
- Parent Release `v5-s-20261102-68099929-1408-41428692617`: 1408 steps; SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; both source Release assets byte-verified and model CPU-loaded.
- **True +128 steps** with seed 92361, cumulative 1536; child model.zip SHA256 `d6e27e7ca3cbde0997cc1bdcb7d1a62b3d19ab9d67f7ffcbde37c204cb4ff843` (separately verified against actual job artifact and public Release API digest). Child metadata matches 1536 steps and pinned engine; ZIP retains PPO optimizer state.
- Permanent unpromoted prerelease: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-experimental-s-20261102-fb6a2c91-resume128-001, includes model.zip (17,525,202 bytes), model.metadata.json, lineage.json, SHA256 receipt, and model-game gate. Unlike 30-day Actions artifact this is versioned Release. **Independent re-download + true optimizer resume from this NEW child Release is not tested; do not claim it.**
- Full raw-artifact provenance: https://github.com/sstxww/reinforcement-learning/actions/runs/41450269678/artifacts/13144104301 ; original job output was inspected and the exact child SHA checked against checkpoint bytes.

## P1/P2 authentic competitive results — NO GAIN
- Original own baseline full game seed 92360, seat0 rank8, 14 turns, 55 decisions, completed, zero truncated; receipt `experiments/s-20261102-fb6a2c91/001-92360.json`, committed from authentic Action.
- Original own **unassisted MaskablePPO** model game seed 92362: seat0 rank8, 16 turns, 129 decisions, completed, zero truncated; child hash `d6e27e7c...`; exact authentic receipt `experiments/s-20261102-fb6a2c91/002-92362.json` copied from real Action artifact. No guard substituted.
- Paired heldout seeds 92370/92371: child model ranks `[8,8]` vs baseline `[8,8]`, delta=0; top4=0%. n=2 is insufficient for competitive strength claims. Model **NOT** Best/Champion.
- Compact reproducible evidence report: `reports/s-20261102-fb6a2c91/001-real-resume-and-eval.json`. No full-game metrics invented; original receipts and report are stored on own branch.

## P2 diagnosis
- Prior real V2: 0 BUY across 74 legal BUY decision exposures; raw IDs1/2 222/248. Pinned source decodes 1 Refresh, 2 Freeze (shop toggle), 7 Cancel, 8..15 Buy. Legal-mask checks affordability.
- Stacked Draft #107 explicitly forced 46 buys in three games, but still `[8,8,8]`; observed Play↔Cancel oscillations. Buying alone not a sufficient fix; root-cause and successful correction unproved.
- Current additional 128 PPO steps did not improve measured rank. Do not scale training blindly; instrument public state changes, Freeze toggles, and Play/Cancel target selection next.

## Merge gates / handoff
- PR #133 is intentionally Draft. The **initial PR CI run #41450393171 failed** before the authentic session receipt existed in the branch; this first-run failure is not evidence that the now-complete branch passes or fails. Re-check latest-head PR CI after the evidence/report commits. Do not merge without fresh exact-head CI, current main compatibility, independent child Release recovery test, and P2 action-loop review.
