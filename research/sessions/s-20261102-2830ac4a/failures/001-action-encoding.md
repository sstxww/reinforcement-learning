# 001 — TavernGym action-range semantics misread

- **Session:** s-20261102-2830ac4a; **PR:** https://github.com/sstxww/reinforcement-learning/pull/28
- **Failure classification:** scientific/strategy correctness error (experiment hypothesis did not match actual action encoding), not a Python exception, CI error, or illegal move.
- **Original execution:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415008425 succeeded, producing seven valid eight-player game receipts. Original code commit `f6cd60f951be78c67e30c6a717e5d600b05d49d8`.
- **Evidence:** fixed upstream `crates/taverngym/src/actions.rs` at `fb61201a557ddd36a411cf44aac51ce4d9b606ce`: `A_SELL = 16`, `A_MAGNETIZE = 126`, sell width 7, magnetize width 70. https://github.com/MCG-NJU/AutoTavern/blob/fb61201a557ddd36a411cf44aac51ce4d9b606ce/crates/taverngym/src/actions.rs
- **Root cause:** experiment incorrectly treated `126:196` as optional Sell. It is Magnetize. Meanwhile `16:23` is Sell; the common baseline does not prioritize that range. The experimental change thus suppressed magnetization, not selling, invalidating the causal label.
- **What remains valid:** real game completion, action legality, engine fingerprints, seeds, placements and decision counts. Neither a sell-policy improvement nor a sell-policy negative result can be inferred.
- **Repair:** correct policy/report semantic naming while retaining legacy module path; add explicit action-space constants, live engine action-name check, unit regression test, shadow baseline disagreement and legal magnetize exposure metrics; rerun all matches.
- **Verification status:** pending corrected workflow and final-head PR CI; update this file with resulting URLs and metrics once verified.
- **Prevent recurrence:** always derive action encoding from exact pinned upstream `Action::encode/decode`, use `taverngym.action_name` runtime assertion and note legacy filenames when correcting experiments.

## Second diagnostic and targeted isolation repair
- First semantic correction run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416193318, success, policy SHA256 `eefea2179896c7bdf94177f5d072b5091aed98512a02446fcebaececd52dd617`.
- Seven new games, same three paired seeds [34201,34202,34203]: both policies ranks [7,8,8], mean 7.6667; acceptance match seed 34200 rank 8. All complete, no illegal actions/truncations.
- Real mask audit: candidate game seed 34200 had 1 baseline disagreement with 0 magnetize-legal observations; seed 34202 likewise had 1 disagreement with 0 magnetize-legal observations. This proves unintended differences remained outside magnetization. In seed 34203, 3 disagreements were all baseline magnetizations.
- **Additional root cause:** after omitting magnetization, the candidate ended a turn before the original baseline's fallback Upgrade check, and used a shorter 60-action cap instead of the baseline's 85. Thus it was not a single-factor test.
- **Second and final meaningful fix:** restore fallback Upgrade-before-End order, match 85-action budget, and fail full games if shadow baseline disagreement count differs from skipped magnetization count. Add unit tests for fallback upgrade, cap and isolated divergence. No third blind retry on this fault signature.
- Verification of the second fix: **pending** own new Actions run and latest-head CI; conclusions remain tentative until they pass.
