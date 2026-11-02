# P2 verified action encoding — pinned source, not a trained-model improvement

Snapshot: 2026-11-02T13:09:15.469Z. Source of truth: read-only upstream pinned commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, `crates/taverngym/src/actions.rs`:

- `A_END=0`
- `A_REFRESH=1` — the paid/free shop Refresh action.
- `A_FREEZE=2` — Freeze/unfreeze shop.
- `A_UPGRADE=3`
- `A_BUY=8` and `N_SHOP=8`, so BUY slots occupy action IDs 8..15.
- The enum and `Action::decode` also map 1→`Refresh` and 2→`Freeze`.

Source: https://github.com/MCG-NJU/AutoTavern/blob/fb61201a557ddd36a411cf44aac51ce4d9b606ce/crates/taverngym/src/actions.rs

The main repository's own `tavern_ai/behavior_probe_ba09e2d4.py` independently uses the same family mapping. The diagnosis is therefore more precise than "unknown ID 1/2 actions."

## Observed behavior in authentic evidence, not newly run by this session

- `reports/s-20261102-83d91476/001-buy-opportunity-report.json`: real V2 PPO model 2 games, ranks [8,8], 74 decisions where BUY was legal, BUY selected 0; 222/248 raw actions were Refresh/Freeze (IDs 1/2). Matched baseline rank [6,7], 33 buys across 48 legal-buy decision exposures. These are correlated exposures.
- `reports/s-20261102-68099929/003-buy-opportunity.json`: newer 1,408-step candidate on seed 99128, 35 legal BUY exposures, 0 selected BUY, 37 Refresh actions; baseline selected 14 buys from 21 legal BUY exposures. Both arms placed eighth.
- This strongly supports **action-selection pathology / compulsive shop control and missing purchases** in tested models. It does NOT prove which PPO component (reward, input normalization, advantage, representation, action probabilities, or training data) caused it, nor that forcibly buying must improve rank.
- Some model evaluations are marked guarded, even when no forced turn-end happened. The strict `paired_evidence_gate_f25a91c8.py` excludes guarded policy labels from raw-model strength claims rather than automatically trusting one game's zero override count.

## Falsifiable next steps before additional PPO budget

1. Confirm model action logits/probabilities on a fixed collection of *public* TavernGym observation states where BUY is legally available, grouped by gold and turn.
2. Track actual gold delta, shop changes, Freeze state and board growth for each model-selected Refresh/Freeze/Buy action; check for no-value loops and whether actions are legal at the time.
3. Make a **single controlled buy-priority intervention** only in a separate candidate, and keep it isolated from model weights. Evaluate on new paired held-out seeds, with guard labels and no unreported fallback.
4. If effect improves behavior, separately test whether imitation of a stronger legal-action teacher leads to actual full-game rank gain. A behavior rescue is not automatically PPO learning or a Champion.

No new model training, games, weights, Champion claims, main modifications or official Arena operations are represented by this report.
