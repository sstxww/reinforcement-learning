# Failure 001 — first PR CI lacked own original full-match receipt

- **Affected exact PR head:** `e60af17ac50e68300b2d08304c6f0199370ca005`.
- **Original failure:** [CI #41512327500](https://github.com/sstxww/reinforcement-learning/actions/runs/41512327500) step `Unit tests and PR evidence` exited 1 after `395 passed, 1 skipped`; first actual error `Missing independent agent game receipt`. The simulated independent run had not yet completed. No code functional test failed.
- **Root cause (verified):** `scripts/check_pr_evidence.py` requires `experiments/<SESSION_ID>/*.json` with actual completed game and matching agent ID; initial Draft branch had no receipt.
- **Fix (not bypass):** successful own [full-match run #41512162363](https://github.com/sstxww/reinforcement-learning/actions/runs/41512162363), original artifact [#13175145044](https://github.com/sstxww/reinforcement-learning/actions/runs/41512162363/artifacts/13175145044) downloaded and checked, genuine baseline and raw model receipts validated. Committed semantically faithful identity/action-summary projections with exact original SHA links and separate report. No fabricated game; complete original trace is still in artifact for 14 days.
- **Retries:** only initial failed CI; new PR HEAD CI auto-trigger after evidence commit, result must be independently checked. Do not count earlier failure as an algorithm defect.
- **Next:** verify newest PR CI and only mark ready after all checks.
