# R001 — prove main direct-merge bypass risk with executable negative evidence

## Hypothesis / baseline
The latest V7 requirement is *global* exclusivity when updating main, not just serial execution by cooperating Actions. GitHub API reported main protected=false and rulesets=[] at source SHA c1b828734527bae6141805581693d890cc3bff94. Issue #182 independently documented concurrent merge during an apparently valid CAS lease; PR #185 proposes a cooperative serial gateway but correctly notes that direct REST merge remains a bypass.

## Implementation / expected falsification
A small read-only stdlib probe queries exact main SHA, protection flag and repository/parent rulesets; outputs a reproducible JSON negative verdict with no credentials, model bytes or edits. Unit tests assert that even an active ruleset does not automatically grant this script global-merge authority. If live API becomes protected, result remains blocked pending proof that all bypass writers are excluded. An isolated read-only workflow runs this test plus a truly completed baseline eight-seat TavernGym game; the baseline is CI infrastructure evidence, *not* model performance.

## Constraints and handoff
Task is intentionally independent of PR #185 files; do not conflict with its owner's active changes. No trained PPO updates, official Release, or candidate model; no ranking claimed. PR readiness requires latest-head CI, downloadable real receipt, repository policy review and integration authorization. No automatic run loops; no main write or protected setting mutation.

## Next step
Retrieve this session's newest branch workflow run/job and original receipt, record seed 99681 / seat 0 / placement only if true game completed. Recheck current main protection and rulesets. If false/empty, ask authorized repository administrator to configure and demonstrate an enforced merge queue / branch rules, or designate exactly one exclusive integrator; until then **no main merge claim**.
