# 001 — Incorrect baseline action-priority assumptions in probe tests

Session: `s-20261102-9a484c57`

- Failure run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415062300
- Failed job: https://github.com/sstxww/reinforcement-learning/actions/runs/41415062300/job/125176791254
- Commit: `f4871f7209eece25983efb3c3bf332ca6eb2af6a`
- Failure stage: `python -m pytest`; 2 failed, 23 passed; real game stage was skipped.
- Exact symptoms: `test_not_upgrade_twice` expected buy action 8 but the baseline chose action 3; `test_unscheduled_turn_and_control_match_baseline` incorrectly expected 8 on a scheduled upgrade turn.
- Root cause: `BaselinePolicy.act` already performs scheduled tavern upgrade (action 3) before buying, but after legal hand plays (46–125). The initial hypothesis and the fixtures overlooked this ordering. An unchanged baseline that correctly returns action 3 must not be declared broken.
- Minimal fix: refine experimental hypothesis to **scheduled upgrade before hand play**; test a mask containing both legal upgrade 3 and play 46. When upgrade already occurred, the candidate must delegate to original baseline behavior. Preserve mandatory discovery choice priority.
- Fix commit: `8f98639e13234ce65ecd69a3dfb2c427160e16d3` (both files in one atomic Git tree commit).
- Re-test run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415219995
- Re-test observation: unit-test step passed on the fixed commit; simulator setup and complete-game evidence remain separate gates.
- Lessons: derive expected actions from current pinned baseline code rather than presumed game strategy; do not delete mismatching tests; preserve the failed CI log.
