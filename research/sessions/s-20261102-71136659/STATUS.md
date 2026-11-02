# V5 R001 — Verified outcome and status

**SESSION_ID:** `s-20261102-71136659`  
**Branch:** `agent/s-20261102-71136659/optimization-001`  
**Run:** [41449601213](https://github.com/sstxww/reinforcement-learning/actions/runs/41449601213)  
**Status:** `blocked_with_evidence` for **durable NEW checkpoint release**, but paired-evidence code/tests and real matches completed; integration PR remains for review.

## Verified operations (2026-11-02 UTC)
- 7 new Python unit tests passed on real GitHub Actions runner; pinned TavernGym 1.1.0 engine `6d8712c93022ba11` verified.
- Independent real baseline game: seed 99371, rank **7**, 14 turns, 46 actions, no simulation guard. Exact receipt: `experiments/s-20261102-71136659/001-99371.json`.
- Parent [1408-step GitHub Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617) downloaded. SHA256 **matched**: `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`.
- Actual CPU MaskablePPO optimizer continuation: **+128 PPO steps, 1408 → 1536**, seed 99372; checkpoint SHA256 `8ab19be62d6f43bce92148c08cb975d355f506fab821b77ed96c2b748705e588`, exact engine metadata in run Artifact. This proves the *source* checkpoint can be resumed, not that the new checkpoint is durably saved.
- Independent full 8-seat real model game seed 99373: rank **8**, turns 15, 126 decisions, valid complete, no combat truncation or time-limit guard. Same seed/seat baseline rank **5**, 14 turns, 53 decisions. Pair delta **+3** (larger is worse), n=1: cannot infer stable population performance or improvement.
- `tavern_ai/paired_evidence_s71136659.py` generated `reports/s-20261102-71136659/001-paired.json`, and refuses premature Champion. Real generated receipts preserved in `experiments/s-20261102-71136659/`.

## Durability blocker
- Release publication command returned `HTTP 403: Resource not accessible by integration` during the step *after* successful PPO and games.
- The fully generated new model.zip **is stored only in short-lived [Actions Artifact #13143508961](https://github.com/sstxww/reinforcement-learning/actions/runs/41449601213/artifacts/13143508961)**, retention 30 days. No new Release tag was created; no permanent model stored. Do not mark recoverable after expiry.
- Real output bytes and full paired report extracted and validated locally from Action Artifact; ZIP artifact is not an immutable Release.
- Failure evidence: `research/sessions/s-20261102-71136659/failures/001-release403.md`.

## Ranking diagnosis
- Additional 128 genuine PPO steps did not improve the one independent observed rank: model 8 vs baseline 5. Prior main legal-buy telemetry: 0 BUY in 35 legal states for 1408-step model; raw 1280-step diagnostic exhibited 2978 HERO_POWER/2977 CANCEL in nonterminating test. These are separate, real logs, not proof of a single causal culprit.
- Proposed priority: instrument public legal BUY with unspent gold and action-state deltas; fix oscillation only after obtaining stable raw model-probe evidence. Do not expand PPO until archival issue and behavioral gate solved.

## Handoff
- Source branch has conservative 81-PR P0 inventory (80 Draft) at `reports/s-20261102-71136659/001-open-pr-audit.json`. Concurrency prevents safe bulk merging. #15 targets #9 draft; must not be merged ahead of dependency.
- Review PR for this read-only, non-promoting paired evidence module plus genuine receipts. Require newest PR-head CI, conflict/dependency and branch-ownership review; don't alter `main` or other agent branches blindly.
- To persist 1536-step weights, a trusted repository maintainer must enable an authorized Release publisher or provide validated durable storage. Do not repeat an identical 403 without a meaningful permissions change.
