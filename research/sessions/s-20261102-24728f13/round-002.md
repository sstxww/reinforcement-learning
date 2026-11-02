# s-20261102-24728f13 · Round 002: genuine PPO action-distribution diagnosis

## Purpose and dependency
After R001 showed candidate 1e-4 required only 66 actions in three heldout complete games versus 759 for reference 3e-4 (with no strength gain), test whether **premature model-selected END_TURN and lack of buy actions** explains the candidate's extremely short traces. This is a diagnostic behavioral hypothesis, not an intervention/causal experiment.

- Session: `s-20261102-24728f13`; own R002 branch: `agent/s-20261102-24728f13/optimization-002`.
- Derived from same session's verified R001 commit `a60fbfbc7133b08d56b58712910689bba58057d9`; original base main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Dependency PR: https://github.com/sstxww/reinforcement-learning/pull/51; own R002 PR: https://github.com/sstxww/reinforcement-learning/pull/60. Do **not** merge this dependent proposal before PR #51 review.
- Scope: new `tavern_ai/action_trace_24728f13.py`, `tests/test_action_trace_24728f13.py`, own bounded workflow `.github/workflows/telemetry-s-20261102-24728f13.yml`, R002 receipts and reports only. No shared module or other Agent edits.

## Engine, inputs and real execution
- TavernGym 1.1.0, verified source hash `6d8712c93022ba11`, observe2 4017 floats + 447 card IDs, action mask 245.
- Inference loads R001's genuinely trained 256-step reference (LR 3e-4) and 256-step candidate (LR 1e-4) weights from run 41416467100 Artifact; checks both SHA256 before real model inference. No training steps in R002.
- Reference SHA256 `8450905bdd1d78e6be68175f9943b16ac840fc9ce2882da4e32791ddb078ad0c`; candidate `802c65e7da2ba42e26e2f2efb55859b91428f1b792428031947484ce95f42f18`.
- New heldout seeds `42174, 42175, 42176`; per arm three **complete eight-seat TavernGym games**, one model-controlled seat versus seven engine bots.
- The same guarded model action-selection protocol as R001 is used (force legal action 0 after 40 intra-turn actions, recording every override). This is not unrestricted model inference.
- Successful dedicated run: https://github.com/sstxww/reinforcement-learning/actions/runs/41418438337, all steps successful including targeted unit tests, game receipt validator, and commit of own results.
- Example mandatory own game `experiments/s-20261102-24728f13/002-42174.json`; six real R002 receipts in that directory, each with full placements, selected-action histogram, per-turn counts and end-turn provenance.
- Compact output: `reports/s-20261102-24728f13/002-action-telemetry.json`.

## Observed full-game results
| Arm | Placements | Mean rank | Total model-seat actions | Model-chosen END_TURN | Forced legal END_TURN | Buy-slot action IDs (8–15) | Longest identical-action streak |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Reference LR 3e-4 | [8,8,7] | 7.67 | 875 | 3 | 21 | 20 | 40 |
| Candidate LR 1e-4 | [8,8,8] | 8.00 | 36 | 21 | 0 | **0** | 2 |

Both arms had 0/3 first and 0/3 top-four results. Mean candidate-minus-reference rank delta is **+0.333** (positive is worse); 3 seeds per arm remain far too few to establish a general strength claim.

Candidate trace details: seed 42174 = 16 actions, 7 model END_TURN, 0 buys; seed 42175 = 9 actions, 7 model END_TURN, 0 buys; seed 42176 = 11 actions, 7 model END_TURN, 0 buys. Model-selected END_TURN is 21/36 = 58.3% of all recorded candidate actions. Reference records 788 `other_action` decisions (raw IDs remain in receipts) and a repeated-action streak reaching the 40-action turn budget; exact semantic root cause not yet identified.

All six receipts report `completed=true`, valid eight-seat placements, zero illegal actions, zero battle truncations and no simulation turn-limit ending. These observations are actual runs, not synthetic unit fixtures.

## Interpretation / failure analysis
- The low-rate candidate exhibited **zero purchases across all three new complete games**, frequent model-selected end turns, and last place every game. This directly supports a descriptive "underacting / premature end" diagnosis on these seeds. It does **not** prove lowering the LR alone caused it, since training variance and a tiny sample limit causal claims.
- The reference exhibits a separate repeated-action symptom despite legal masks and a 40-action safety override. It did purchase minions but still ranked last or seventh. Investigate specific repeatedly selected raw action IDs and whether they have meaningful state-changing effects.
- Training/executing more steps, unconditionally increasing action count or forcing purchases is **not** already demonstrated as a cure.

## Persistence and next steps
- No fresh weights or new training steps in R002; use same R001 temporary model Artifact expiring Dec 2, 2026. Prior checkpoint reload success: https://github.com/sstxww/reinforcement-learning/actions/runs/41417110915.
- R002 result Artifact (receipts/compact telemetry only) is temporary. No permanent model backup is claimed.
- New failure mode is **behavioral**, not CI/runtime crash: see `research/sessions/s-20261102-24728f13/failures/002-action-utilization.md`.
- Next falsifiable study: measure whether high-frequency repeated reference raw actions cause non-progress/no-state-change while separately tracking candidate actionable purchase opportunities; only then design an isolated policy intervention and test heldout full-game placements.
- Before integration check final-head CI of PR #60; any head checks prior to this documentation commit are not sufficient.
