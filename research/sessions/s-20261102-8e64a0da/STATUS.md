# s-20261102-8e64a0da / STATUS (verified, 2026-11-02)

## P0 actually merged
- [PR #102](https://github.com/sstxww/reinforcement-learning/pull/102) squash-merged into main SHA `1afd8297e3c661bee3117ac5301b1ca08d64869b` with exact-head gate. Postmerge main [CI #41449457029](https://github.com/sstxww/reinforcement-learning/actions/runs/41449457029) SUCCESS. No direct push to main.
- Parallel agents independently merged PR #75; do not duplicate. PR #93 remained Draft due stale four-candidate assertions vs canonical five.

## P1 real executed model restore/continuation
- Own dedicated [GitHub Actions #41450146951](https://github.com/sstxww/reinforcement-learning/actions/runs/41450146951): **SUCCESS** (not a proposal).
- Source canonical unpromoted Release: `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; both actual assets re-downloaded, matched trusted index; CPU load success.
- Actual `128` further PPO steps: `1408 -> 1536` cumulative. Independent saved-model reload and Adam optimizer continuity `88 -> 96` both verified.
- New checkpoint SHA256: `c3bc7cd952bbf02fb4a15e3866a13c98bc9f1486eb3de35fd119b1651f81a73a`.
- Durable [experimental GitHub prerelease](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-smoke-s-20261102-8e64a0da-resume128) `v5-smoke-s-20261102-8e64a0da-resume128`, `model.zip`, `model.metadata.json`, real JSON reports; downloaded again and byte-compared. Not Champion.
- Actual own true eight-seat games: baseline seed `90311`, rank **8**, 13 turns, 39 decisions, `experiments/s-20261102-8e64a0da/001-baseline-90311.json`; unguarded raw resumed PPO model seed `90312`, rank **8**, 16 turns, 128 decisions, `experiments/s-20261102-8e64a0da/002-model-90312.json`. Both genuine completed games with no combat truncation/turn-limit end. **Different seeds: NOT a paired comparison.**
- Own full truthful report: `reports/s-20261102-8e64a0da/001-resume-smoke.json`, guard/complete-game status `reports/s-20261102-8e64a0da/002-model-game-status.json`.
- Actual new PPO steps confirmed: **128**, two own completed eight-seat games (one baseline, one unguarded model). Model strength improvement **NOT verified**; `champion` and `best` remain null; model should not be promoted.

## P2 evidence and remaining gates
- Current 1408-step candidate seed 99128: 35 masked-legal-buy decisions with zero chosen Buy; baseline 14 Buy; both rank 8. Source: `reports/s-20261102-68099929/003-buy-opportunity.json`.
- Separate V2 1280-step unguarded seed 87102: 2978 HeroPower, 2977 Cancel over 6000 decisions; raw game incomplete, rank not defined. Opt-in guarded completed games still ranked 8. Sources: `reports/s-20261102-ba09e2d4/002-action-opportunities.json` and `005-guarded-evaluation-summary.json`.
- Root-cause hypothesis: legal Buy omission + nonprogressing choice loops; mechanism and causal ranking contribution require paired heldout, economics/hand/board traces. Do not scale training solely because engineering resume passed.
- Own [PR #146](https://github.com/sstxww/reinforcement-learning/pull/146) **Draft** until latest-HEAD PR-triggered full-game CI success and integration review, current-main compatibility recheck. GitHub-generated bot PR CI `41450942544` concluded `action_required` with zero jobs; this human-authored status-update commit should generate a new PR CI and needs independent confirmation. Do not treat `action_required` as tests passed.
