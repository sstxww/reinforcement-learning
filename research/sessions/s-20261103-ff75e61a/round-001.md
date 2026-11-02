# R001 — V7 registered raw PPO vs baseline (new paired seed 99541)

## Scope / hypothesis

Prior real V5 1408-step Release `a73d24c...db2632` has independently completed raw rank-eight games; in historical paired seed 99385 it scored 8 versus baseline 7, and many earlier traces showed no BUY despite legal BUY masks. The causal root is **unknown**. A new raw complete-game sample versus same-seed baseline can extend descriptive evidence, but **n=1 cannot imply generalization or improvement**.

## Protocol

- Pull exact immutable registered `model.zip` and `model.metadata.json` from V5 1408-step Release, validate expected model SHA256 before model inference.
- Use pinned TavernGym 1.1.0 / engine hash `6d8712c93022ba11`, seat 0, seven scripted bots, seed 99541.
- Execute an independently verified baseline full game; execute completely raw deterministic PPO with no forced end, buy assistance, human decisions, substitution or fallback.
- Real full game only when `Game.is_over()`; aborted game gets a separate failure record without rank. Source engine contract 4017 floats, 447 cards, 245 masked actions.
- For two successfully completed authentic receipts, execute the existing `paired_receipt_gate_v5.compare` (n=1 descriptive, not statistically powered) and preserve original files and summary as temporary Actions artifact, then commit verified records.
- Timeout <=35 minutes, read-only GitHub job token, unique concurrency group, one execution per branch path, no workflow self-push. Do **not** consume extra PPO training or publish/promote models on a known rank-eight candidate without first verifying raw behavior.

## Existing evidence / independent P0 review

Existing [PR #168](https://github.com/sstxww/reinforcement-learning/pull/168) documents actual seed 99385 raw model rank 8, baseline rank 7. This is an external source, not this round's own run. Independently verified [PR #185 latest CI](https://github.com/sstxww/reinforcement-learning/actions/runs/41512690022) failed due to missing original own game receipt; posted [review](https://github.com/sstxww/reinforcement-learning/pull/185#pullrequestreview-5742385698) on potential stale CI rerun gate. No merges, no tests or games falsely claimed.

## Expected next work

Read run job/logs and archive original Action artifacts, record exact HEAD SHA, seed, model SHA, completed/aborted separately; if raw fails, preserve error with budget/timeout and do not label it eighth. Check whether current exact main SHA and CI changed and leave an integrator-ready note. Evaluate BUY-opportunity state traces as the next isolated hypothesis only if this seed provides actionable new signal.
