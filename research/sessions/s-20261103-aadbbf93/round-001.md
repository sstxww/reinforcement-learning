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

## Verified own run and CI failure diagnosis (after PR #184)

- **Own real complete TavernGym eight-seat baseline**, authenticated [run 41512218951](https://github.com/sstxww/reinforcement-learning/actions/runs/41512218951) **completed/success**, job 125506666383: pinned engine installed, V7 regression tests passed, `Game.is_over()` true, independent baseline seed **99673**, controlled seat 0 rank **7**, placements `[7,2,1,3,8,5,4,6]`, **16** turns and **43** decisions, `truncated_combats=0`, `turn_limit_end=false`. No PPO weights were used; new training steps remain zero.
- Original artifact [13173676456](https://github.com/sstxww/reinforcement-learning/actions/runs/41512218951/artifacts/13173676456) downloaded independently; ZIP SHA256 `65e353644d2426b315c8a6affc1cd26d8ee5905f315e3eb107928f9a400ddac6`; contained genuine `001-99673.json` **516 bytes**, SHA256 `17f6ed79b982123e2e04cb9df6af8b96e60d074591643a659dfe5a1ded4c775e`, committed without modification at `experiments/s-20261103-aadbbf93/001-99673.json` in commit `d86404a044ee56bb1db758dd87a25fb158b93ca3`.
- **Actual first PR CI failure:** [run 41512463850](https://github.com/sstxww/reinforcement-learning/actions/runs/41512463850) on HEAD `74f01cd613f3209881382c5ca9c6138ceb2f47e1` completed with failure at `scripts/check_pr_evidence.py` because `Missing independent agent game receipt`; unit tests themselves reported **393 passed, 1 skipped**. This expected evidence gap was repaired by committing the original Action artifact. Do not call this earlier red run green. New latest-head CI must be checked after final report commits.
- Concurrent sequential branch pushes caused pending review workflow runs to be cancelled (not successful games). Only completed run **41512218951** counts as own independent true game evidence.
- No model training, candidate Release, Best/Champion promotion, main merge or postmerge CI verification occurred in this session yet.
