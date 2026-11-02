# s-20261102-f17ed915 R001 — conservative evaluation-integrity integration

## Evidence and exact scope
- Session branch `agent/s-20261102-f17ed915/optimization-001`, initial main SHA `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
- Gmail V5 TXT fully read. Verified project rules under AGENTS.md, SESSION_PROTOCOL, CLOSED_LOOP; examined current trainer, evaluator, Releases and unpromoted 1,408-step model registry.
- Initial open PR scan 75. PR #102 was independently merged mid-review at `1afd8297e3c661bee3117ac5301b1ca08d64869b`, with latest-head CI passing; did not duplicate the merge. Stacked PR #15 depends on Draft PR #9. No safe unclaimed existing PR automatically approved.
- Avoid overlap with other sessions' checkpoint, legal-BUY and trainer work. This round isolates a missing provenance gate in **paired evaluation reporting** only.

## Methodology
- Read existing committed authentic paired TavernGym 1.1.0 / observe2 receipts for seeds 99125, 99126, 99127, both arms from identical per-seed source SHAs.
- Candidate fixed model SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` (1,408-step experimental Release, not Champion).
- Strict audit refuses incomplete/guarded eight-seat matches, rank permutations invalid, wrong engine, mismatched pair seeds, source/agent mismatches, mixed model weights, reported fallback and (when supplied) training seed leakage.
- Metrics include placement, top4 rate and Wilson 95% uncertainty, first-place rate, mean turns/decisions and per-seed paired deltas. Schema-1 legacy game receipts lack explicit fallback/illegal-action counters, so label `unknown_schema1_omits_counters`; do not label as independently established raw model performance.
- Existing heldout ranks: candidate [8,8,8], baseline [6,8,8], paired difference +0.667 rank (positive means model worse); n=3 is descriptive, seat0 only.
- Own isolated workflow must run 13 offline regression checks, replay the committed six genuine receipts, bootstrap pinned engine and generate **one NEW authentic eight-seat baseline match** with strict receipt check. No large model training while P0–P2 remain under review.
- Do not confuse replaying six receipts with running six new games. Training steps this round = 0.

## Pending gates
Remote workflow, actual receipt, exact-head PR CI, integration review and main post-merge CI must be independently checked. No Champion/best promotion and no ranked Arena.
