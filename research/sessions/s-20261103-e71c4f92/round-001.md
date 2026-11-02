# Round 001 — read-only same-seed real-game control experiment

Session s-20261103-e71c4f92; ROLE=WORKER; TASK_KEY=evaluation/paired-raw-v5-1408-seed-99385.

## P0 and priority
Main `3602f64b798bb51dcf69ef5964fe0b4c4cd39495` already integrates canonical Release restore #117, staged resumable save #125, rank integrity #152, and Champion gates #138; those are OTHER sessions' contributions. The only ready #15 is stacked on Draft #9. Do not merge or create another canonical trainer. Concurrent #161/#164/#165 already cover SHA-bound resume, schema-2 metadata and Release token scope.

## Falsifiable experiment
The existing 1408-step registered raw V5 PPO scored eighth in held-out games and showed repeated REFRESH/FREEZE and zero buys in prior real-game diagnostics (#162 and #161). Seed 99385 has not appeared in the PR search at start. This independent P3 probe compares raw 1408-step weights and baseline on SAME public simulator seed, seat zero, seven scripted bots. A paired one-seed result is descriptive, NOT statistically significant and not an architecture diagnosis.

The job retrieves immutable Release assets via existing verified `release_restore_entry`, checks known SHA256, executes each entire eight-seat match, stores only `game.is_over()` complete receipts, checks the full placement permutation, verifies seed/strategy/SHA, and uploads original JSON. Any incomplete match produces failure evidence without a fake rank. It does not use guard, fallback, forced purchasing, training, Arena, or shared files.

## Run / review gates
Workflow: `.github/workflows/v61-paired-s-20261103-e71c4f92.yml`, triggered once per branch update; `reports/s-20261103-e71c4f92/` artifact on every result, max 65 minutes CPU, read-only token. Exact Actions URL, results, authentic receipt hashes and validation must be appended **after** successful execution; do not claim before proof. A PR without committed authentic receipt remains Draft/blocked.

## Real costs and outcome at commit
Own PPO steps: **0**. Own completed model games at commit: **0**. Own finished baseline games at commit: **0**. Stored new models: **0**; unpromoted Release source reused read-only. No claim of rank or performance gain. This file is an exact starting ledger, not a fabricated success report.
