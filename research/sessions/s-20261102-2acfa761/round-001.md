# s-20261102-2acfa761 Round 001 — P0/P1 integration extraction

Branch: `agent/s-20261102-2acfa761/optimization-001`; base: `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
Scope: new isolated pairing statistics, own regression fixtures, own workflow, own research handoff only.

P0 findings: main is moving under multiple agent sessions; PR #93 was reviewed and left Draft due to stale exactly-four-model assumptions and main's already integrated dual-asset Release verifier. PR #15 is non-Draft but targets `agent/learning/v1` and depends on Draft #9; do not merge directly to main. No unsafe main merge attempted.

P1 change: offline receipt-level pairing with seed permutation, stable model SHA and completion checks; reports assisted/raw provenance, top-four rate, mean place and descriptive paired uncertainty. Tests are synthetic and must never count as actual matches.

P2 evidence: register latest experimental checkpoint 1,408 steps, heldout 8/8/8, no trusted Champion; branch #103 reports 521 legal-BUY-exposure decisions with 0 buys but guarded full-game results. Root causes (reward, observations, action ranking) are not proven. No change in training budget or weights.

Actual PPO updates: 0. New model: none. Model-only completed games: 0. Planned actual baseline receipt from isolated Actions seed 96271 is **pending** until run and committed receipt are independently verified.
Next: verify workflow receipt and final-head CI; consider integration only after review and current-main compatibility. No official ranked Arena.
