# Rank-eight root-cause observation: action taxonomy

**Status: partially diagnosed; not a causal conclusion.**

- **Verified code defect in diagnostic labels:** the merged `tavern_ai/behavior_audit_v5_880b8a71.py` reports raw action 1 (Refresh), 2 (Freeze), 7 (Cancel) and 196–244 (Move) under `other`, despite the engine-confirmed family table being available in `mechanics_audit_f3af3b4d.py`. Before the fix, the resulting action-category histograms could conceal the model's actual high-frequency loops.
- **Previously recorded real game evidence, not rerun this session:** Actions #41428098018, two V2 model-only games rank [8,8], 0 BUY in 74 BUY-mask-legal decision exposures, 222 of 248 raw choices action IDs 1/2. Same-seed baseline rank [6,7], 33 BUY with 48 BUY-mask-legal decision exposures. See `reports/s-20261102-83d91476/001-buy-opportunity-report.json`.
- **Other negative outcomes:** canonical registry's 1408-step heldout [8,8,8], paired baseline [6,8,8]; candidate remains unpromoted. Later forced-buy experiments report continued eighth-place outcomes. Hence preventing non-buy actions alone is *not proven* sufficient to improve strength.
- **Unresolved hypothesis:** repeated Refresh/Freeze/Cancel/Play or Move decisions may waste economy/action budget or fail to change material game state, but per-turn gold, board and the action-mask trajectory must be captured in actual live games before claiming the dominant cause. Another hypothesis is that PPO learns to exploit shaping while neglecting BUY and board growth.
- **This code change:** restore correct action family labels and distinguish raw proposal from executed guard override. No improvement, game or training completion is claimed for this session at this stage.
