# Failure F001 — PR evidence check before own real game receipt was committed

- Signature: `Missing independent agent game receipt` in `scripts/check_pr_evidence.py`.
- Observed [CI run 41510142950](https://github.com/sstxww/reinforcement-learning/actions/runs/41510142950) on branch head `1cec734c47358e9ed865daa8620736050799444f`: pytest **337 passed, 1 skipped**, then evidence step exited code 1. Engine bootstrap/full-game CI was skipped.
- Root cause: original branch intentionally lacked a purported receipt until the separate authentic runner completed. An earlier synthetic/fabricated receipt would have passed repository gate incorrectly.
- Actual fix: own [Actions run 41510089011](https://github.com/sstxww/reinforcement-learning/actions/runs/41510089011) completed both real eight-seat games on seed 99385, strict validation and a matched-source model check. Authenticated original logs and Artifact 13172728337 supply the records; now add `experiments/s-20261103-e71c4f92/001-99385-{baseline,model}.json` to the branch and recheck exact-head PR CI.
- Retries: this is the first substantive fix. Do not rerun the same failed commit as-is. No match or training was falsely credited before evidence existed.
