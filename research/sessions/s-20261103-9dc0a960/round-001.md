# Round 001 — V6.1 actual P0 audit and bounded raw PPO economy probe

## Scope and main
WORKER s-20261103-9dc0a960; parent main `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`. Branch `agent/s-20261103-9dc0a960/optimization-001`. P0 checks: #15 is non-Draft but depends on #9 Draft and targets its head branch, not main; #165/#167 are active overlapping Release-training work, so do **not** copy them or merge them. Main trainer is now manual-only Release restored.

## Controlled falsifiable comparison
Input 1408-step candidate from [published unpromoted Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617), SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Engine pinned `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patched observe2 source `6d8712c93022ba11`, actions 245, floats 4017, cards 447. Fixed novel seed 43837, control seat 0. Pure deterministic masked PPO versus separately run scripted baseline. Record raw ID (not guessed semantic), legal BUY band 8..15, end-with-buy, unchanged public state, and liveness budgets. No hidden information, no forced end, fallback or invented placement.

## Honest gate
- Synthetic tests must pass first, followed by true TavernGym full eight-seat baseline and raw PPO probe through [session workflow](https://github.com/sstxww/reinforcement-learning/actions/workflows/v61-raw-economy-9dc0a960.yml).
- True model completion and per-game placements may be written only from the engine; incomplete raw probe is a failed budget-limited diagnostic and not a game receipt.
- No new PPO steps, model archive, or promotion is claimed by creation of this branch; `train.yml` is shared main-only and other sessions already have Release-resume experiments under test.
- Full model/baseline comparison is descriptive (n=1 if both complete); no causal verdict or competitive improvement claimed.
- If CI/unit/engine fails, capture exact job URL and diagnosis, not green by assumption.

## Next hypothesis
If the raw model has mask-legal BUY exposures but selects none, check mask/action-to-semantic alignment and policy logits before considering additional PPO steps. If model completes/BUYs, investigate which decision context or seat/seed makes it fail, maintaining fixed independent seeds.

## Actual executed run #41510804758 (verified against uploaded artifact)

- [Own Actions run](https://github.com/sstxww/reinforcement-learning/actions/runs/41510804758): **failure**, by design because pure PPO did not finish, not because pinned TavernGym or tests failed. Regression, engine verification, baseline full eight-seat game, published 1408-weight download/SHA256 all passed.
- Actual baseline receipt: `experiments/s-20261103-9dc0a960/001-43837.json`; seed 43837; scripted baseline (not model); 13 turns; 31 decisions; completed; placements `[8,2,5,7,3,6,4,1]`; rank 8; 0 truncated combats. Original receipt SHA256 `0c2aed429f1305f3e4e66530747e34a9312872cc18b69005b216aa378273f7a3`.
- Actual unassisted PPO diagnostic `reports/s-20261103-9dc0a960/raw-ppo-43837-summary.json`: 223 decisions, 88 mask-legal BUY exposures, **0 BUY**, 6 END_TURN actions, 61 play-band actions, 1 upgrade; action histogram 1:31, 2:60, 7:60, 46:61, 0:6, 3:1, 31:1, 32:3. Turn 7 exceeded the 120-own-decisions-per-turn cap; `completed=false`, `model_placement=null`, **no model receipt**. Exposure denominator is repeated decision masks, not independent affordable shopping opportunities. This is a single-seed observational failure, not a causal decoder proof.
- [Original unabridged raw report and baseline receipt Artifact](https://github.com/sstxww/reinforcement-learning/actions/runs/41510804758/artifacts/13172359996); original report SHA256 `69327fc4b3d939b1137da301c4cef2f37a9820afcbf7988f40bbdcd8c29ef939`; artifact ZIP SHA256 `5028ef418ddb4ed9a333dcc82f26eb23c2ea7395ea808309c1da140a65a2ce89`; Artifacts expire on 2026-12-02, so the decisive summary and baseline receipt are committed to this isolated branch.
- Real **new** PPO training steps: **0**; **new** model Release: **none**; Best/Champion: unchanged; paired model versus baseline placement comparison: **not computable** because raw PPO did not complete.
- Failure log: `research/sessions/s-20261103-9dc0a960/failures/002-raw-turn-liveness.md`. No deterministic rerun of the same model SHA/seed without substantive change.
- Action: preserve as `blocked_with_evidence`, review pinned engine semantics for raw action 1/2/7/46 and policy probabilities before a modified small-scale experiment. Do not promote this model.
