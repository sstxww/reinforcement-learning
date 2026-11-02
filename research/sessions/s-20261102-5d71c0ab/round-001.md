# Round 001 — P0/P1 integration gate and rank-eight evidence

Session: `s-20261102-5d71c0ab`. Branch: `agent/s-20261102-5d71c0ab/optimization-001`.
Initial main base: `1afd8297e3c661bee3117ac5301b1ca08d64869b`. Repository: `sstxww/reinforcement-learning`.

## Actual initial audit (2026-11-02)
- Open PRs at first snapshot: 75, including 74 Draft and one non-Draft (#15).
- #15 targets `agent/learning/v1` and depends on Draft #9, so merging it straight into main is unsafe.
- Main previously passed full-match CI at `db5e23ae8c218808821327d806b05d2604cfadfb` (run 41432038040). Main subsequently advanced; no claim that this initial run covers later commits.
- Fifteen published Releases were visible; presence of model assets does not independently prove restorability.
- Canonical `models/registry.json` has no Best/Champion. It indexes a 1,408-step unpromoted candidate with three heldout ranks 8/8/8 vs baseline 6/8/8. These are historical recorded outcomes, NOT this session's new games.
- An actionable promotion integrity gap: `model_registry.read_registry` previously allowed Champion based only on a `review_status=verified` label; it did not require the separate durability/load/resume/match/competitive-evidence flags.

## Change in this round
- Harden only the existing `tavern_ai/model_registry.py` Champion gate (no new competing registry).
- Add synthetic offline regression tests that reject absent/false/string evidence flags and dangling role references.
- Use one bounded session-unique workflow to run an actual eight-seat baseline match, independently preflight a published 1,408-step model, and collect two paired legal-BUY comparisons.
- No Arena ranked play; no new PPO training until P0–P2 results justify it. No claim of Champion or strength gain.

## Execution state
This file is a pre-run handoff, not a completed-game receipt. Check the exact commit's Actions run and downloaded `outputs/*.json` before treating the match or diagnosis as verified. If CI completes, add immutable evidence and update STATUS in this branch before requesting merge.

## Existing PR prioritization
- A (ready to merge now): none proven; Draft and dependency gates block immediate integration.
- B (repair/dependencies): #9 before #15; other checkpoint compatibility drafts need latest-HEAD checks.
- C (more evaluation): many model and BC experiments report small or uncertain effects.
- D (negative experiments): #12, #19, #51, #60, #65, #71, #74 and other explicitly negative drafts must not be promoted.
- E (stacked/duplicates): #103→#107, #90→#105, #62→#65, #72→#76 and overlapping Release-checkpoint PRs require integration review.

## Next stop
Verify the new run, save full receipt under `experiments/s-20261102-5d71c0ab/`, record raw vs guarded behavior without mixing their ranks, then review main HEAD and CI before considering a merge. Continue PPO only after meaningful behavior diagnosis and reliable checkpoint restoration.
