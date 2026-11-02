# V6.1 independent WORKER status — s-20261103-9dc0a960

- Role: WORKER; not elected INTEGRATOR, so never merge `main` or alter its shared training workflow, champion registry, or another session's refs.
- TASK_KEY: `p2/raw-ppo-unassisted-buy-liveness-seed43837` — read-only raw model economic-action diagnosis, **no competing trainer implementation**.
- Starting main SHA: `3602f64b798bb51dcf69ef5964fe0b4c4cd39495` (2026-11-02 19:23Z approx).
- Branch: `agent/s-20261103-9dc0a960/optimization-001`.
- Protocol: Gmail 2026-11-02 19:21:22Z; full 22,229-byte `AutoTavern-AI-V6.1-多会话并发闭环自训练完整提示词.txt` read.
- P0 audit: 117 open PRs in 100+17 REST pages; 116 Draft. #15 is the only ready PR, based on `agent/learning/v1` and dependent on unmerged Draft #9: **not safe to merge**. #165 and #167 address overlapping Release/write-token and training integrity; this branch does not touch `.github/workflows/train.yml`, `tavern_ai/train.py`, `tavern_ai/evaluate.py`, or `models/registry.json`.
- Current main training is manual-only registered Release restore; latest main full-match CI for this exact SHA still needs check. No claim that main P1 is fully verified by us.
- Model diagnostic input: immutable published unpromoted 1408-step candidate `v5-s-20261102-68099929-1408-41428692617`, expected SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. This is **not** Best/Champion.
- Own fixed held-out seed: 43837, controlled seat 0; raw deterministic MaskablePPO, no assisted fallback; separate baseline on same seed. Max 480 raw model seat decisions and max 120 own decisions/turn.
- Hypothesis: failure to select mask-legal BUY is measurable in raw policy without assuming causation, public-gold decoding, or forcing a BUY. Incomplete raw games are failures, never rank 8.
- Files changed: isolated `tavern_ai/v61_raw_economy_9dc0a960.py`, focused `tests/test_v61_raw_economy_9dc0a960.py`, session-exclusive workflow and records.
- Training new PPO steps: **0** (P0 and P2 gating before redundant expansion); no new checkpoint or durable Release claim; no Arena matches.
- Current state: branch implementation, independent engine run and receipt pending actual Actions execution. Do not claim completion or improvement before verified run and artifact.
- Next priority: inspect exact raw model buy-opportunity/mask-liveness report, compare genuine baseline completion, then narrow the decoder/mask hypothesis only if grounded by raw actions.

## Actual executed run #41510804758 (verified against uploaded artifact)

- [Own Actions run](https://github.com/sstxww/reinforcement-learning/actions/runs/41510804758): **failure**, by design because pure PPO did not finish, not because pinned TavernGym or tests failed. Regression, engine verification, baseline full eight-seat game, published 1408-weight download/SHA256 all passed.
- Actual baseline receipt: `experiments/s-20261103-9dc0a960/001-43837.json`; seed 43837; scripted baseline (not model); 13 turns; 31 decisions; completed; placements `[8,2,5,7,3,6,4,1]`; rank 8; 0 truncated combats. Original receipt SHA256 `0c2aed429f1305f3e4e66530747e34a9312872cc18b69005b216aa378273f7a3`.
- Actual unassisted PPO diagnostic `reports/s-20261103-9dc0a960/raw-ppo-43837-summary.json`: 223 decisions, 88 mask-legal BUY exposures, **0 BUY**, 6 END_TURN actions, 61 play-band actions, 1 upgrade; action histogram 1:31, 2:60, 7:60, 46:61, 0:6, 3:1, 31:1, 32:3. Turn 7 exceeded the 120-own-decisions-per-turn cap; `completed=false`, `model_placement=null`, **no model receipt**. Exposure denominator is repeated decision masks, not independent affordable shopping opportunities. This is a single-seed observational failure, not a causal decoder proof.
- [Original unabridged raw report and baseline receipt Artifact](https://github.com/sstxww/reinforcement-learning/actions/runs/41510804758/artifacts/13172359996); original report SHA256 `69327fc4b3d939b1137da301c4cef2f37a9820afcbf7988f40bbdcd8c29ef939`; artifact ZIP SHA256 `5028ef418ddb4ed9a333dcc82f26eb23c2ea7395ea808309c1da140a65a2ce89`; Artifacts expire on 2026-12-02, so the decisive summary and baseline receipt are committed to this isolated branch.
- Real **new** PPO training steps: **0**; **new** model Release: **none**; Best/Champion: unchanged; paired model versus baseline placement comparison: **not computable** because raw PPO did not complete.
- Failure log: `research/sessions/s-20261103-9dc0a960/failures/002-raw-turn-liveness.md`. No deterministic rerun of the same model SHA/seed without substantive change.
- Action: preserve as `blocked_with_evidence`, review pinned engine semantics for raw action 1/2/7/46 and policy probabilities before a modified small-scale experiment. Do not promote this model.
