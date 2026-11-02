# Failure 001 — inverted baseline upgrade priority

- Session: `s-20261102-9c034841`
- Commit: `05fb27e35d133af07566f2505295772095b8ee6d`
- Actual run: https://github.com/sstxww/reinforcement-learning/actions/runs/41414939740
- Job log: https://github.com/sstxww/reinforcement-learning/actions/runs/41414939740/job/125176391112
- Signature: `test_after_three_actions_returns_to_base_policy` asserted 8 but observed 3; 23 tests passed, 1 failed; no real TavernGym installation/game attempted.
- Reproduction: `python -m pytest tests/test_upgrade_priority_s_20261102_9c034841.py` with mask legal actions 0, 3, 8, turn 5 and actions_used 3.
- Root cause: an incorrect reading of main `BaselinePolicy.act`; after play/discover, it prioritizes action 3 on turns {2,5,7,9,11} **before** buy(8..15). Initial probe changed nothing substantive on that decision. Original test expectation was wrong.
- Material correction: invert candidate arm to *buy before upgrade*, but only when the baseline selected upgrade, preserving discover and play priorities; fix tests to reflect both the real original priority and the altered decision.
- Retest: **SUCCESS**, corrected commit `fea0eb39e6880b732bc2896ca1a47d126fe79de7`, https://github.com/sstxww/reinforcement-learning/actions/runs/41415146112. Entire regression suite passed (24 tests); real TavernGym 1.1.0 installed, mandatory own candidate match + 4 paired seeds (9 complete matches) all succeeded; mistake is documented and test retained.
- Scope: only this session's isolated module, tests and reports. No changes to shared policy or other sessions.
