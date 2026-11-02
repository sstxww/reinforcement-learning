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
