# s-20261102-860ff0fd STATUS — R001

Status: **1536 steps restored and trained; model-only seed 93873 complete rank8; independent heldout seed 93874 FAILED full-game safety limit**. Definitive general-robustness/strength improvement **NOT VERIFIED**.

Successful source training: https://github.com/sstxww/reinforcement-learning/actions/runs/41449658176 (1408→1536 PPO steps), model SHA `2a0aa260c08b087b1bd703a102af7b6a25a1785e17a2b11bbf854ea48f5b99eb`; own baseline seed 93871 rank8 and model seed 93873 rank8 receipts committed.

Independent restore/custody run https://github.com/sstxww/reinforcement-learning/actions/runs/41450970156: engine, ZIP optimizer state, digest, CPU model load, source game verified, then FAIL on first heldout seed 93874 due `Full-game safety limit exceeded`. Paired scoreboard unavailable, no fabricated scores. This is a model policy progression failure, not corrupt weights.

Attempt to preserve this known-bad but structurally resumable checkpoint on an immutable **REJECTED** Release via new isolated archive workflow. No durable publication claim until exact byte roundtrip verified.

PR #110 latest-head CI https://github.com/sstxww/reinforcement-learning/actions/runs/41450979261 **SUCCESS**, but remains Draft pending full continuous lineage review and no-bad-model promotion. Concurrent main integrated PR #75 and others; duplicate #68 held. No direct main push; Champion remains unset.
