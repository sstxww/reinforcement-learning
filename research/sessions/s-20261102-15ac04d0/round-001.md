# V5 s-20261102-15ac04d0 — round 001

## Provenance and authorization
- Allowed write target: sstxww/reinforcement-learning only; no upstream, A11, desktop, or ranked Arena use.
- Start main: db5e23ae8c218808821327d806b05d2604cfadfb
- Source instructions: Gmail V5 TXT (953 lines).
- P0 audit: 75 open PRs at snapshot, 74 Draft; only non-Draft #15 depends on #9, still Draft. No unsafe merge performed.
- Latest indexed experimental candidate: V5 1408-step GitHub Release, best/champion null. No new candidate trained by this session.
- Linked evidence: reports/s-20261102-83d91476/001-buy-opportunity-report.json; Draft PR #107. Evidence supports masked-legal BUY omission and action-family loops, not a complete causal rank-8 theory.

## Scoped actual changes
- tavern_ai/paired_receipt_gate_v5.py (fail-closed same-seed and seat model/baseline receipt comparison, guard labeling, descriptive paired-bootstrap interval, no automatic promotion).
- tests/test_paired_receipt_gate_v5_15ac04d0.py (17 synthetic cases and negative integrity cases; synthetic cases are never represented as real games).
- .github/workflows/v5-paired-evidence-s-20261102-15ac04d0.yml (own bounded push-triggered full-game gate, exact engine bootstrap, 30-day receipt Artifact).
- research/knowledge/proposals/s-20261102-15ac04d0-001.md (source-backed P0/P2 proposal).
- Does not edit shared trainer/registry/CI or other sessions' paths.

## Real execution status (to be updated against exact Actions outcome)
- First live Actions 41449566645 failed a synthetic test fixture, not simulator logic: the Python assignment mutated a list index before locating the old rank. 16/17 tests passed. No full game ran in that failure.
- Fix commit 6439f190a98706c4247593269a73bfa187f07718 uses precomputed rank index.
- Second live Actions 41449685070 **SUCCESS**: 17 own tests, entire repository tests (234 passed, 1 skipped), fixed TavernGym version/source contract, genuine completed eight-seat baseline game, source-generated receipt artifact 13143807609.
- Genuine own complete match: experiments/s-20261102-15ac04d0/001-93431.json, copied byte-for-byte in fields from successful Actions runner output. Seed 93431, own seat 0 rank 7, turns 14, decisions 65, placements [7,6,4,5,3,2,1,8], zero combat truncations, no game-turn guard. Rules baseline policy only; NOT PPO competitive evidence. Action source commit 6439f190a98706c4247593269a73bfa187f07718. Artifact https://github.com/sstxww/reinforcement-learning/actions/runs/41449685070/artifacts/13143807609.
- Own training: **0** PPO steps; no new model/checkpoint or Champion.
- PR CI and postmerge main CI: **not yet claimed**.

## Integration gate
Do not treat a passing baseline canary as model strength. Before merge, require authentic own full-game receipt committed under experiments/s-20261102-15ac04d0, complete own Action, independent exact-head PR CI and conflict check. If these are unavailable, keep Draft.

## Next scientific test
Use verified durable V2/V5 weights for seed/seat matched paired raw receipts, log legal BUY exposures, actual BUY and Play/Cancel repetitions, and isolate one causal repair. Until that evidence exists, avoid blind PPO budget expansion. No ranked Arena.
