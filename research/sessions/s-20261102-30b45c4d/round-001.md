# Round 001 — public mechanism catalog + action-mask evidence

## Hypothesis
The first useful step toward strategic learning is a provenance-preserving mapping of the **observable** card vocabulary and **actual** legal-action semantics. Counting "all cards" as playable, or treating card text as proven scripts, introduces mechanistic false labels.

## Base and isolation
- Session: `s-20261102-30b45c4d`
- Base: `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Branch: `agent/s-20261102-30b45c4d/optimization-001`
- Pinned upstream: `fb61201a557ddd36a411cf44aac51ce4d9b606ce`
- Engine contract: 1.1.0 / `6d8712c93022ba11`, observe2 `4017/447/245`.
- Own new source/tests/workflow only; no shared baseline, PPO, main, model or other session changes.

## Verified source-side insight (before experiment)
- `crates/taverngym/src/actions.rs` explicitly defines 245 actions. Sell = 16..22; Play = 46..125; Magnetize = 126..195; Move = 196..244.
- `crates/taverngym/src/obs.rs` maps `CardId(i)` to observed card index `i+1`; 0 is padding. `crates/taverngym-py/src/lib.rs` exports `N_CARDS = db().len() + 1`.
- `crates/taverngym/data/cards.json` at pinned source includes 3,983 card records; unpooled cards exist. Effects in text/keywords have not been independently execution-tested.

## Planned bounded experiment (not yet a result)
1. `python -m pytest -q tests/test_mechanics_audit_s_30b45c4d.py`
2. `bash scripts/bootstrap_engine.sh`
3. `python -m tavern_ai.mechanics_audit_s_30b45c4d --source vendor/AutoTavern/crates/taverngym/data/cards.json --seed 83171 --output-dir artifacts/s-20261102-30b45c4d`
4. `python -m tavern_ai.validate_receipt artifacts/s-20261102-30b45c4d/receipt.json`
5. Preserve generated JSON card index as an expiring Action Artifact; commit only small summary and real receipt to own branch.

## Evidence fields
- Model trained: no (0 updates / 0 timesteps).
- Evaluated policy: unchanged `BaselinePolicy`; one seat vs seven official bots.
- Candidate-mean-placement delta: not applicable; no new policy is evaluated.
- Current evidence: script and unit tests committed; **full-match run pending**.
- Training checkpoint: none; not needed for this mechanism audit.
- Future use: derive **separately validated** mechanism labels and teacher pretraining features.

## Scientific guardrails
- Action-family observations are descriptive and constrained by states reached under the baseline, not comprehensive legality proofs for all game states.
- The catalog does not prove individual Battlecry/Deathrattle/Spellcraft script behavior.
- A single actual match cannot establish ranking strength or improve Arena MMR.
