# Failure 001 — inverted baseline upgrade priority

- Session: `s-20261102-9c034841`
- Commit: `05fb27e35d133af07566f2505295772095b8ee6d`
- Actual run: https://github.com/sstxww/reinforcement-learning/actions/runs/41414939740
- Job log: https://github.com/sstxww/reinforcement-learning/actions/runs/41414939740/job/125176391112
- Signature: `test_after_three_actions_returns_to_base_policy` asserted 8 but observed 3; 23 tests passed, 1 failed; no real TavernGym installation/game attempted.
- Reproduction: `python -m pytest tests/test_upgrade_priority_s_20261102_9c034841.py` with mask legal actions 0, 3, 8, turn 5 and actions_used 3.
- Root cause: an incorrect reading of main `BaselinePolicy.act`; after play/discover, it prioritizes action 3 on turns {2,5,7,9,11} **before** buy(8..15). Initial probe changed nothing substantive on that decision. Original test expectation was wrong.
- Material correction: invert candidate arm to *buy before upgrade*, but only when the baseline selected upgrade, preserving discover and play priorities; fix tests to reflect both the real original priority and the altered decision.
- Retest: pending distinct commit/workflow; **no result claimed**.
- Scope: only this session's isolated module, tests and reports. No changes to shared policy or other sessions.
