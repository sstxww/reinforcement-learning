# STATUS — s-20261103-5ac92b95 / V6.1 R001
- Role: **WORKER**; task key `evaluation/paired-guard-alias-integrity` (path-scoped, **not** an atomic exclusive lease).
- Base `main`: `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`.
- Branch: `agent/s-20261103-5ac92b95/optimization-001`.
- Status: **authentic original games completed**, DRAFT awaiting refreshed exact-head PR CI and integrator review.
- Scope: narrow guard/fallback counter aliases in `tavern_ai/paired_receipt_gate_v5.py`; isolated regression test, workflow and own research paths. No main push, shared workflow, registry or model changes.
- P0: main already merged #116, #117, #125, #138, #140, #152, #154, #157 and #162 at snapshot; #15 is Ready but stacked on Draft #9; do not merge. Concurrent Drafts #161/#164/#165/#167 own other fixes; not copied/merged.
- Hypothesis: actual telemetry `guard_forced_ends` and canonical evaluator `fallback_actions` can be nonzero while paired gate marks the receipt raw model, risking inflated research claims. Regression must reject assisted raw games.
- Source model: registry Latest unpromoted V5 1408-step Release, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`; Best/Champion null (snapshot only).
- Own PPO updates: **0**. Own model Release: **none**. Own training and model-game placement: **not claimed**. Authentic model and baseline canaries both completed in independent GitHub Actions 41510322107; see exact original receipts in experiments/, committed after downloading Artifact 13173380337.
- Next: capture and validate own full eight-seat receipt from the exact workflow run, commit unmodified receipt to our branch, rerun PR CI and publish verified result.

- **Verified own successful Actions**: https://github.com/sstxww/reinforcement-learning/actions/runs/41510322107 (job 125500201100). Artifact 13173380337, retention 14 days, retrieved before copying original JSON into git.
- Original complete eight-seat seed **99753 / seat 0**: raw/unassisted model rank **8**, 121 decisions, 16 turns, placements [8,6,7,1,3,2,4,5]; baseline rank **7**, 39 decisions, 13 turns, placements [7,2,8,4,1,3,5,6]. Both ended, no truncated combats or artificial turn-limit, no fallback.
- Paired n=1: model-baseline placement delta **+1** (worse), no 95% interval, no improvement/promotability claimed. Model SHA256 = a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632; existing Release 1408 steps only. New training steps=0; new Release=none.
- Original PR CI https://github.com/sstxww/reinforcement-learning/actions/runs/41510410611: 353 tests passed / 1 skipped but required own receipt was not yet committed; not a Python failure. Genuine receipt is now included in this follow-up commit; new PR CI result must be checked independently.
