# Round 001 — exact PR evidence gate

## Work inherited
Read complete V7 Gmail TXT (32,014-byte source). Inspected live repo, AGENTS.md and V1 coordination docs, registered model, train.yml, canonical evaluation/receipt paths, PRs #15/#165/#172/#173/#175/#176, main-head Actions and existing Release inventory.

## Hypothesis and code
A previous-successful Actions run or empty/action_required job can be mistaken for current-HEAD real-game evidence when sessions race. A read-only gate requiring the exact PR head, current main, real completed `CI - full-match gate / tests-and-full-match` jobs and a same-session receipt will fail closed on this class of mistake. It does **not** make the repository branch-protected or implement CAS merge coordination.

Implemented `scripts/v7_merge_gate_aadbbf93.py` and synthetic mutation regressions `tests/test_v7_merge_gate_aadbbf93.py`. Synthetic fixture only tests the gate and is **not** a real match result. Added finite read-only workflow `.github/workflows/v7-review-s-20261103-aadbbf93.yml` to run own tests and actual pinned eight-seat baseline seed 99673.

## Evidence and limits
- Main at first inspection `c5edec2e3261dacdf3908796ebfe0457fb76c02e`; already moved to `990acd21d598a34a554a80c50089a8f1a9423ac4` while this session worked.
- PR #176 latest-head `6444f75d6b4dba073e82e624e42b53c3790a30ca` full-match CI [41510729988](https://github.com/sstxww/reinforcement-learning/actions/runs/41510729988) succeeded, but its exact main compatibility and exclusive merge lease not proven here.
- Repo branch protection GET returned 403 via integration; branch list metadata reported `protected=false`. No visible fixed coordination ref from branch search; **never claim globally exclusive lock**.
- No own game, newly trained model, successful CI or Release yet at this reporting checkpoint; complete those only after actual run evidence arrives.
- Main V5 1408-step candidate historical source SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, historical raw model eighth place, not improved by this audit.

## Next test
Open own PR against current main, inspect actual own workflow and PR CI. Do not merge based on this document or synthetic tests. If a complete baseline artifact is generated, validate and commit the original unchanged and verify final HEAD CI. Follow up with read-only audit of PR #176 to assist the real integrator.
