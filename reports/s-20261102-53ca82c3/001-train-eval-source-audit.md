# Training / evaluation source audit — V5 P1/P2 (2026-11-02)

Session: s-20261102-53ca82c3. Read only the current main versions of `tavern_ai/train.py`, `tavern_ai/env.py`, `tavern_ai/evaluate.py`, `tavern_ai/canary.py`, and `.github/workflows/train.yml`. These are source-confirmed engineering gaps, **not** claims of causal model underperformance.

## Confirmed integration gaps

1. `train.yml` only restores `v1-model` from last successful Actions artifact. That artifact has a 90-day expiry; its restore branch silently initializes random weights when download is missing/fails. There is no fail-closed durable Release recovery in main.
2. `train.py` compares `model.metadata.json` against exact `verify_engine()` output on resume, then loads SB3's MaskablePPO. It does **not** independently validate an out-of-band model SHA256, immutable model origin, registry entry, optimizer-state integrity or an atomic checkpoint publish transaction.
3. `evaluate.py` runs a fixed controlled seat (seat 0) on consecutive seeds and reports mean rank/top4/first; does not produce seat-rotation, confidence intervals, action-fallback counts or round-level action opportunity rates. A paired baseline option is present but no promotion gate is enforced.
4. `canary.py` verifies every model action against the native legal mask and requires the game to finish; however it only stores compact final placement/decisions, not the economic/action trace needed to explain repeated eighth place.
5. `train.yml` uses heldout seeds starting 24000 for every run. Reusing the same heldout seeds repeatedly risks adaptive model-selection leakage when tuning based on observed evaluations.

## Non-overlap choice

Other sessions have active V5 work on checkpoint preflight, Releases, model registry, and behavior diagnostics. Rather than overwrite shared trainer/workflow files or run another random-from-scratch PPO, this session integrated the independent safe cleanup fragment of #8, with a bounded real-game verification workflow.

## Recommended next acceptance tests (not performed here)

- Download immutable Release checkpoint and trusted digest; verify zip load, optimizer resume, engine hash, action space and total timesteps.
- Fail intentionally on missing artifact/release or bad hash without retraining from scratch; preserve prior checkpoint.
- Compare baseline, old and challenger on independent seed/seat rotations with confidence intervals, explicit model-vs-fallback action counts.
- For every controlled decision log whether any BUY action 8..15 is legal and whether END_TURN selected; aggregate gold/board/hand state by round to distinguish no-op collapse from affordability issues.

**Gating conclusion:** no certification of a durable latest model or stronger Champion from this audit; do not approve expanded training until independent restoration and real-model behavior evidence are available.
