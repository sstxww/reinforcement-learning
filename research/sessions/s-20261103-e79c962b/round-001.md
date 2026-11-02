# Round 001 — exact-head CI preflight

## Hypothesis
In a repo with over a hundred parallel PRs, stale green status from an earlier commit can be misinterpreted as a green check for the current PR head and main. A small read-only fail-closed audit can filter this class of error **before** the human/leased integrator's full safety checklist.

## Implementation / verification
- Base main `990acd21d598a34a554a80c50089a8f1a9423ac4`.
- New script `scripts/v7_pr_head_audit.py` performs read-only GitHub REST GET for PR, branch main and exact-HEAD check runs. Caller must provide both expected SHAs. Unavailable/partial checks fail closed; success only means `needs_integrator_review`, never `merge_authorized`.
- Seven synthetic pytest regressions passed locally; they are NOT TavernGym match receipts.
- Owned branch workflow will run one pinned TavernGym 1.1.0 baseline full eight-seat match seed 99773 with 35-minute cap and temporary 30-day Artifact; not raw MaskablePPO performance. Status remains unverified until Actions success and receipt inspection.
- Existing registered Release `v5-s-20261102-68099929-1408-41428692617` SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` not modified; 0 new training steps, no optimizer resume, no new model or Release.
- Main status changed during inspection: `3a745c6` merged #176, then `990acd21`. Existing #165, #173, #177, #172 have meaningful overlap/security blockers.

## Limits / decision
Checks API may not attach the same run to a PR HEAD as to its synthetic merge commit; false-negative is deliberate, not success. This preflight does not validate the complete eight-seat receipt, reviewer independence, secrets, current merge base or lease. No direct main merge without unique integrator right.

## Next
Inspect own workflow run logs and generated authentic receipt, commit receipt after verification, refresh handoff, open non-Draft PR once evidence gates are satisfied. Otherwise preserve blocked status and exact run URL. Do not start duplicate training merely to get a Release; the main optimizer-resume and rank-8 problems need a separate allocated budget and ownership.
