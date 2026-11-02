# Failure #001 — first PR CI had no independent completed game receipt

- **Failure category:** evidence ordering, **not** Python unit test failure and **not** PPO behavior.
- **Exact PR HEAD:** `4dc7c03487e578cbdfc64ab80d65672ed86e3ee3`; PR [#216](https://github.com/sstxww/reinforcement-learning/pull/216).
- **Workflow:** [CI #41513809602](https://github.com/sstxww/reinforcement-learning/actions/runs/41513809602), job `125512087506`.
- **Actual log:** `390 passed, 1 skipped in 0.74s`, then `scripts/check_pr_evidence.py` printed `Missing independent agent game receipt`, exit 1. Engine/full-match steps skipped. This run is FAILED and shall never be called green.
- **Cause:** the unique branch originally opened PR before its separate bounded real-game workflow completed. PR checker requires an independently generated complete `experiments/<SESSION_ID>/*.json` match, which did not yet exist. This is a required protective gate, not a bug to bypass.
- **Evidence-backed remediation (one meaningful fix):** original [branch Action #41513736888](https://github.com/sstxww/reinforcement-learning/actions/runs/41513736888) subsequently completed SUCCESS; retrieved exact [Artifact #13173373888](https://github.com/sstxww/reinforcement-learning/actions/runs/41513736888/artifacts/13173373888) and validated original complete baseline JSON seed 99831, seat 0, 8-seat permutation; committed that file unchanged as a genuine baseline game receipt. The real unassisted raw model diagnostic is separate and is **not** a canonical receipt.
- **Remaining verification:** check latest HEAD PR CI to prove this fix, and inspect any later failures in their own run. No invented receipt and no CI bypass.
