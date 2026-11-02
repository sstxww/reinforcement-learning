# R001: Native-card static mechanism provenance audit

Session: s-20261102-ada5c379
Branch: agent/s-20261102-ada5c379/optimization-001
Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
Training steps: 0. Candidate policy: none. Checkpoint: none.

## Hypothesis
The pinned TavernGym native Python ABI exposes structured card kind,
race, keyword, mechanic, stats and pool metadata by embedding index.
Extracting it produces source-backed offline mechanism features without
inventing text-based rules or exposing hidden game-state information.

The 447 card observation slots are NOT the number of card definitions.

## Provenance
Upstream commit fb61201a557ddd36a411cf44aac51ce4d9b606ce
TavernGym 1.1.0, engine source hash 6d8712c93022ba11.
Observe2 patch sha256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0
Ruleset tg36-bc45cfc55a0e5cd6c14c.
Contract catalog sha256 c4c42e6ce5060e1b79fbcd5f4edbf6d17495f0f52690072481d690610f7ef6d7
Sources: crates/taverngym-py/src/lib.rs, cards.rs, types.rs,
and crates/taverngym/tests/mechanics.rs.

## Scope
New module, tests, session-owned workflow and receipt/report paths only.
No shared baseline, PPO model, common workflow, or other agent files changed.
Four selected source-backed keyword/mechanic examples; these are only
schema checks, not confirmation of every effect's trigger semantics.

## Planned finite run
Install pinned engine, execute unit tests, generate runtime catalog
artifact and digest, then run a real 8-seat baseline infrastructure canary
at seed 110221. Validate and commit this session's receipt and summary.
CI must verify latest commit. Run budget: one + at most two substantive fixes.

Status: PENDING cloud execution; no verified result at this point.
Model placement: N/A. Competitive improvement: NOT MEASURED.
Next: tactical ability diagnostics on held-out real-engine situations.
