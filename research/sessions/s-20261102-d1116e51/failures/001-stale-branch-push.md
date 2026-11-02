# Incident 001 — authentic game evidence push rejected (stale branch)

- Session: `s-20261102-d1116e51`; branch: `agent/s-20261102-d1116e51/optimization-001`
- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416380388
- Job: https://github.com/sstxww/reinforcement-learning/actions/runs/41416380388/job/125181131001
- Source Commit under test: `d3c25e60c92cc4d99a0547588e298a279ba23038`
- Classification: **Git branch persistence race**, not game/test/training defect.

## Actual log signature

```text
! [rejected] HEAD -> agent/s-20261102-d1116e51/optimization-001 (fetch first)
error: failed to push some refs to 'https://github.com/sstxww/reinforcement-learning'
hint: Updates were rejected because the remote contains work that you do not
```

The runner had checked out source at `d3c25e6`. While the job ran, the same session committed `STATUS.md`, `round-001.md`, and its experience proposal to the branch. Its new result commit therefore lacked the new branch commits as ancestors, and Git correctly rejected a non-fast-forward update. No other agent was involved; no force push attempted.

## Real results before failure

- Unit and regression tests: **success**.
- Exact TavernGym bootstrap: **success**, version 1.1.0/source `6d8712c93022ba11`.
- One candidate and three pairs of baseline/candidate real eight-seat games: **7/7 completed**.
- Candidate canary seed 49001: rank 7, 56 decisions, 10 choice interventions.
- Paired baseline ranks [7,7,7], candidate ranks [8,8,8]; all valid masks, no truncations or guard.
- Upload Artifact: **success**, ID `13128375430`, expires 2026-12-02. ZIP SHA256 `0f3276f00f68b5609b6305edcb5e6e8eb1dd53176e089b265b75301afe8b478e`.

## Actual recovery

1. Downloaded the exact Actions artifact through the GitHub connector.
2. Inspected all eight JSON payloads, confirming completed true, distinct seeds/policies, valid eight-seat placement permutations, zero illegal actions, zero combat truncations and zero turn-limit flags.
3. Recreated the seven authentic game receipts and one paired summary on **this** branch using GitHub connector calls, preserving actual seeds, recorded run SHA, timestamps, placements, decisions and policy SHA.
4. Updated `.github/workflows/experiment-s-20261102-d1116e51.yml` with `git fetch` + `git rebase` of its own branch before evidence push, and one bounded retry; committed with `[skip ci]` to avoid an unnecessary second 7-game run.

**Validation statement:** receipt recovery completed and original upstream simulation completed. The YAML rebase safeguard itself has **not** been re-executed; do not claim the entire earlier workflow run succeeded. No original experiment was retried. No other branch modified.

## Prevention

Do not modify a session branch between Actions checkout and evidence auto-push unless the runner fetches/rebases. Better, submit the preliminary handoff before starting expensive games, or write receipts first and write handoff later. Always retain an Artifact when the final branch write fails.
