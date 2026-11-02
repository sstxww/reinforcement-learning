# Round 001 — Candidate checkpoint write must not overwrite another run

Session s-20261103-822bc450. TASK_KEY checkpoint/candidate-save-no-clobber. Initial main 990acd21d598a34a554a80c50089a8f1a9423ac4. Branch agent/s-20261103-822bc450/optimization-001.

## Inheritance and hypothesis
Read the complete V7 TXT and live main; #117 and #125 already protect registered Release restoration and staged saves, while #175 uniquely owns Release restore no-clobber. Canonical tavern_ai/checkpoint_writer.py still uses os.replace() for training *output* pairs. Another run writing the same candidate path could clobber existing model bytes or metadata. This is an independent fail-closed custody bug, not an improvement to PPO rank.

## Code
Changed only writer commit 84d0f001216710e760c02ef811a8888490ac8004, plus own synthetic tests 8f9554d600fab49ef59548d532d83d0707e47085. Exclusive hard links fail if either output already exists; rollback first link on second-link failure without deleting unrelated replacements. Crashes between the two hardlinks are not a single transaction: subsequent saves fail closed and require investigation.

## Evidence
Seven new synthetic tests; isolated GitHub Actions and pinned-engine baseline receipt to be appended only when completed. Until then test_status = pending, game_status = pending. No model loaded, trained, restored or published by our session yet. No rank improvement claimed.

## Baseline and limits
Registered source 1408-step V5 unpromoted Release SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632, not used as our training input. Historic eight-place failures supported in merged #176 and #164; not attributed to checkpoint writer. Separate research needed for raw policy nonprogress.

## Next
Verify isolated real-game output, commit original receipt, run exact-head independent PR CI and check new main compatibility. Only merge with valid main integration lease and complete gates.
