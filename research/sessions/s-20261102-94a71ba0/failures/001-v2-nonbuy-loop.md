# R001 — Real V2 PPO missing purchases and repeated legal actions

**Signature:** Model has zero purchases although BUY is legal on 42 decisions (7 turns); repeated Move(197) 68 times, Freeze(2) 60 and Refresh(1) 37. Model seat0 placed 8th in same-seed 83501, while rule Baseline purchased 16 times and placed 3rd.

**Source:** successful real full-game GitHub run https://github.com/sstxww/reinforcement-learning/actions/runs/41428347003 . Model Release `v2-learning-41413557445`, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. Engine source hash `6d8712c93022ba11`. Receipt `experiments/s-20261102-94a71ba0/001-83501-model.json`, trace `reports/s-20261102-94a71ba0/001-v2-opportunities.json`.

**Behavioral failure classification:** legal-action utility/pathological loops, not invalid action mask; no prohibited hidden-state access. **No causal training failure proven.** Unconditional action repetitions may consume decisions without improving economy, but this trace does not record before/after game-state hashes to prove action-level no-ops.

**Safety:** one explicit forced END at action cap 80, so `performance_class=guarded_model_not_raw`. Game fully completed and mask legal; never label as uninterrupted raw model performance.

**Next falsification:** compare pre/post publicly observable game state, money, board and shop for repeated Move/Freeze/Refresh; test the hypothesis that policy uses state-ineffective legal moves. After validated permanent Release restoration, train separate controlled action-value/BC candidate. Use independent seeds/seat rotations, paired baseline, guard intervention rate and real full games; do not promote from this n=1.

**No correction yet:** This is diagnosis, not a silent policy fix. No new PPO steps or Champion update. Initial PR CI failed only because evidence receipts did not exist at PR creation; runner then completed and committed valid receipts. Latest-head independent full-match CI remains a separate acceptance gate.
