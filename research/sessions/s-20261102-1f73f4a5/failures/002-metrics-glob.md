# Failure 002 — metrics JSON mistaken for real match receipt

- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41420778736
- Failure signature: `ValueError: Incomplete/non-TavernGym game` after `21 passed`, from `scripts/check_pr_evidence.py` calling `validate` on an aggregate metrics `summary.json`.
- Cause: PR contract intentionally validates **every** `experiments/<SESSION_ID>/*.json` as a full complete match. First experiment's `summary.json` was stored alongside the four real receipts.
- Correct fix: isolate the summary at `experiments/s-20261102-1f73f4a5/reports/summary.json`; only true teacher and guarded student match JSONs stay at the top level. Modify private experiment code and workflow output/staging paths. Common main receipt validator unchanged.
- Real matches themselves remained genuine; no dummy JSON. Historical successful training run #41420063194 is preserved; retry source/workflow in own branch only, once, with independent workflow concurrency.
- Final recheck: PENDING new full experiment and PR CI; two-fix limit not exceeded.
