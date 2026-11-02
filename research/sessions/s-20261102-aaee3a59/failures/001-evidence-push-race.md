# Failure 001 — concurrent branch evidence push rejected (non-fast-forward)

Session: s-20261102-aaee3a59; round 001.
Source: genuine GitHub Actions run [41449990914](https://github.com/sstxww/reinforcement-learning/actions/runs/41449990914), job 125292531483, log inspected after completion.

## Observed facts
- Exact pinned TavernGym 1.1.0 engine bootstrap passed: source `6d8712c93022ba11`, observe2 4017/447/245, card vocabulary 3984.
- Five targeted synthetic restore/source-integrity tests passed.
- **Real complete eight-seat baseline canary passed**, seed 94431, controlled seat 0 **rank 6**, placements `[6,7,5,8,4,1,3,2]`, turns 15, decisions 51, zero combat truncation, `turn_limit_end=false`. `python -m tavern_ai.validate_receipt` reported verified match.
- The subsequent `git push origin HEAD:agent/s-20261102-aaee3a59/optimization-001` was rejected **non-fast-forward** because the workflow started on commit `d4c7141c468e3b27f91cd5363fe45b56400ca51a` and the same session authored additional GitHub commits to its branch during the engine build. This is an OWN-session race, not an attempted overwrite of another Agent.
- Therefore **Release download, PPO continuation, model canary and checkpoint persistence were skipped**. This run completed **0 PPO learning steps**, **0 model-controlled complete games**. Do not claim otherwise.
- Initial generic PR CI [41450165759](https://github.com/sstxww/reinforcement-learning/actions/runs/41450165759) separately passed **240** tests (1 skipped) but failed mandatory PR evidence check because its snapshot preceded the real receipt.

## Recovery actually committed
- Parsed and sanity-checked the machine-generated JSON line from the genuine job log, preserved its original fields unmodified and committed under `experiments/s-20261102-aaee3a59/001-94431.json` via authenticated GitHub API, commit `54ca24381fc0bf7bbecaa201809de64facbe4635`. No fabricated receipt or synthetic game.
- Modified isolated smoke workflow to compare replayed deterministic match fields against archived receipt, restore working-tree receipt after replay, and rebase on the current session branch before any **future model-only evidence** push (rather than force-push).
- Corrected `train.py` to hash the parent checkpoint *before* saving child (including when caller uses a common path).
- New workflow and PR CI runs were automatically queued from code updates. Their success has **not** been claimed in this report.

## Guardrails
No main merge, no Champion promotion, no new durable trained checkpoint, no official Arena, no upstream write. Do not restart bulk PPO or interpret a complete baseline match as model performance. If later workflow fails, read the actual job log before further fixes; at most two distinct root-cause retries.
