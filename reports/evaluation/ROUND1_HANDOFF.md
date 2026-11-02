# Round 1 evaluation handoff (2026-11-02)

Branch: `agent/evaluation/v1`; PR: https://github.com/sstxww/reinforcement-learning/pull/7

Verified genuine TavernGym 1.1.0 full match, engine source `6d8712c93022ba11`:
`experiments/evaluation/seed-13001-593bf502965e.json`; seed 13001, 15 turns, 51 seat-0 decisions, placements `[4,1,8,7,2,5,6,3]`; no truncated combats or turn-limit ending.

The evaluation implementation adds seeded summaries and optional baseline comparison. Earlier tests failed because `evaluate()` call signature disagreed with tests; subsequent commits changed the interface. Confirm the **latest head** still passes unit tests and PR engine-backed complete-match CI. Report sample sizes, seed IDs, average rank, top-four rate and first-place rate. One rank-4 result does not demonstrate improvement.
