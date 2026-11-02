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


## Verified execution results (2026-11-02, after real Actions run)
- Successful real workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41421973239
- Verified code head in workflow: 03ce60c33f2f4aaab135a168ea752ad0d08e798d
- Offline ABI regressions, pinned engine installation, full test suite, catalog
  extraction, full-game canary, receipt validation, evidence commit and artifact
  upload ALL passed according to the latest workflow steps.
- Actual native card records: 3983 (embedding index 0 is padding).
- Static input width per card: 66.
- Runtime catalog digest: dd20591d5af542187d25bbca0824daae2adfd496423c2a03a78743187b532ab3.
- Selected upstream-test metadata cases: 4 / 4 verified against native table.
- Distribution: 2596 minions, 143 heroes, 176 hero powers,
  208 tavern spells, and other categories. See compact JSON for all counts.
- Actual completed **baseline infrastructure** match:
  experiments/s-20261102-ada5c379/001-110221.json
- Seed 110221; 15 turns, 51 own decisions, placements [8,2,4,7,6,5,1,3].
- Own seat 0 rank **8**, 0 truncated combats, no turn-limit end.
- This was NOT a candidate-model match. No trained model, no performance delta;
  a single baseline match establishes only the infrastructure and ABI checks.
- Compact report:
  reports/s-20261102-ada5c379/001-card-summary.json
- Complete card table retained in the run's 30-day Artifact only; do NOT
  claim permanent model or dataset persistence from this expiry-bound artifact.
- First workflow version failed YAML parsing (run 41421891537, zero Jobs):
  malformed escape in the artifact name. Corrected in 03ce60c; next run
  executed successfully. No model failure was involved.
- Training timesteps: 0. Model checkpoint: NONE. Model strength: NOT EVALUATED.
- Result: engineering/catalog validation SUCCESS, strategy improvement UNTESTED.
- PR and review: required before any curated knowledge promotion.
