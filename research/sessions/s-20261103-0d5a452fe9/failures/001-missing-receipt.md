# R001 CI gate failure — independent completed game receipt not yet committed

- Session: s-20261103-0d5a452fe9; task: audit/main-direct-merge-enforcement.
- First PR CI run: https://github.com/sstxww/reinforcement-learning/actions/runs/41513338684
- Job: 125510474682, exact PR head f60c3dc3d6d79edcafa43da326871954a7e40860; base main c1b828734527bae6141805581693d890cc3bff94.
- Original error from Actions logs: `Missing independent agent game receipt` in `Unit tests and PR evidence`.
- Important positive fact: `python -m pytest` completed **395 passed, 1 skipped** before the receipt-gate error. That pass count includes 10 newly added P0 gate tests, but is not a valid entire CI pass.
- Consequence: pinned-engine setup and complete eight-seat CI stage were **skipped** in this run. No CI eight-seat receipt and no PPO placement can be inferred.
- Root cause: own independent baseline workflow was queued at the time; no original completed receipt existed in `experiments/s-20261103-0d5a452fe9`. The gate correctly rejected the premature PR and must not be weakened.
- Intended source of original evidence: https://github.com/sstxww/reinforcement-learning/actions/runs/41513189439, workflow commit d26b4d7cc96ff5db33bb803a628b0467eae1d996; baseline-only seed 99681, seat 0 vs seven bots. As last seen this was queued, not completed.
- Fix attempt count: **0**; next valid fix is to retrieve and validate the actual full-game JSON (if that workflow completes), commit its bytes unchanged to `experiments/s-20261103-0d5a452fe9/001-99681.json`, then wait for/check **latest** PR-head CI. Do not generate a synthetic receipt or disable `check_pr_evidence.py`.
- Current status: blocked_by_missing_real_game_receipt, not a coding regression; no merge-authority claim. Independent explicit main branch protection still absent; no bypass of merge safety or champion gate.
