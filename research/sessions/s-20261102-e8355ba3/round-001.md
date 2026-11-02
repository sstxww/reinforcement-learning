# V5 Round 001 — P0 integration triage and P2 evidence integrity

Session: `s-20261102-e8355ba3`. Parent main when own branch was created: `1afd8297e3c661bee3117ac5301b1ca08d64869b`. Unique branch: `agent/s-20261102-e8355ba3/optimization-001`. Read full 27,248-byte Gmail AutoTavern-AI V5 TXT on 2026-11-02.

## Actual P0 inspection, time-bounded

- First main HEAD `db5e23ae8c218808821327d806b05d2604cfadfb` with successful full-match CI [41432038040](https://github.com/sstxww/reinforcement-learning/actions/runs/41432038040). Main moved repeatedly while reviewing and BEFORE this branch was created; never reuse an old HEAD for merger.
- Initial live PR listing: 75 open; 74 Draft; 15 GitHub Releases. The lone non-Draft #15 depends on still-Draft #9. Draft #8 is conflicted and spans shared infrastructure. #93 and #95 have observed current-head PR CI success but remain Draft; do not override author review gates.
- Concurrent integrator `s-20261102-8e64a0da` explicitly claimed PR #102 (issue comment on that PR), so this session did **not** attempt to merge it.
- No PR was merged by this session; no exclusive integration ownership acquired. Draft/stacked/conflicted PRs cannot be merged merely to lower the open count. All observations are snapshots rather than a fully completed 75-PR security/diff audit.

## P1 checkpoint and evaluation state

- `models/registry.json` lists an experimental unpromoted latest 1,408-step candidate in GitHub Release `v5-s-20261102-68099929-1408-41428692617`, SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`. Main's recorded paired held-out ranks for the candidate are [8,8,8] versus [6,8,8] for baseline. This session did not download or independently reload that 17MB model; no Champion is established.
- Main trainer and evaluator still have known Release fail-closed resume / seat-rotation / uncertainty / fallback-telemetry gaps, described in `reports/s-20261102-53ca82c3/001-train-eval-source-audit.md`. Other agents have active P1 work; this session made **no shared trainer, evaluator or model registry mutations**.
- All model releases require a real downloaded-hash/CPU load/optimizer continuation/complete game chain before declaring reusable training state.

## P2 raw-versus-guarded provenance gate (this session's independent deliverable)

Verified from existing main source reports (NOT newly generated games):
- `reports/s-20261102-ba09e2d4/002-action-opportunities.json`: unmodified V2 model could not complete the raw bounded game after 6,000 decisions, including 2,978 HeroPower and 2,977 Cancel actions, 10 decision-level legally available BUY masks and zero purchases. Game placement is NULL, not 8.
- `reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json`: only a **guarded** version reached complete matches on 87102/87103 (ranks [8,8], four total guard interventions), baseline on same seeds ranked [5,7], no documented strength gain.
- Added standalone pure-Python `tavern_ai/guarded_evidence_gate_e8355ba3.py` plus tamper/regression tests, preserving exact source-model SHA, engine hash, paired seeds, action-counter sums, game completion and fallback separation. The tool refuses relabeling failed raw model trace as a finished game, or candidate promotion based on this weak evidence. Does not alter game policy or masks.
- Bounded isolated [Actions workflow 41449911575](https://github.com/sstxww/reinforcement-learning/actions/runs/41449911575) tests the reconciler, bootstraps pinned TavernGym, and requests one authentic 8-seat baseline canary seed 93031. Treat game receipt/CI as **pending until independently checked**.

## Resource budget, caveats, next steps

PPO training steps this session: **0**. New model-controlled games: **0**. Model checkpoints created/saved: **0**. Champion promotion: **none**. No formal ranked Arena access. No overwrite of any other session's branch, receipt or checkpoint.

Acceptance: verify Actions 41449911575 complete-success and copy only its exact full-game JSON; run head-specific PR CI after filing a Draft PR; keep Draft until full engineering/security review. Continue P1 Release recovery and raw-policy behavior diagnosis before any PPO expansion. A single baseline canary is an engineering gate, not model performance evidence.
