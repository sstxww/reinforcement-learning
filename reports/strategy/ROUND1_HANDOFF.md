# Round 1 strategy handoff (2026-11-02)

Branch: `agent/strategy/v1`; PR: https://github.com/sstxww/reinforcement-learning/pull/6

Verified genuine TavernGym 1.1.0 full match, engine source `6d8712c93022ba11`:
`experiments/strategy/seed-11001-9a621f90f601.json`; seed 11001, 14 turns, 52 seat-0 decisions, placements `[6,3,4,5,7,2,1,8]`; no truncated combats or turn-limit ending.

Independent single-paired-seed experiment is recorded in `reports/strategy/v1.json`: seed 1301, V0 rank 8, V1 rank 8, both 47 decisions. This is **no demonstrated improvement**. Strategy PR remains draft pending current-head CI and stronger paired-seed assessment. Earlier tests had a signature/priority mismatch; inspect latest CI before merging. Do not promote a model or assert Arena performance.
