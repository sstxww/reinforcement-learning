# s-20261102-dfa88e31 — Round 001 / V5 P0 receipt integrity integration

## Source and scope
- Read latest Gmail subject AutoTavern-AI V5 and the complete 27,248-byte TXT instructions.
- Own isolated branch: `agent/s-20261102-dfa88e31/optimization-001`; base main `1afd8297e3c661bee3117ac5301b1ca08d64869b`.
- Write scope: strict PR receipt validation gate, synthetic regression tests, unique isolated real-game workflow, own receipts and research handoff. No direct main/upstream/Arena writes.
- No model weights, trainer configuration, shared registry or Champion changed.

## P0 independent inventory
- At initial API snapshot: main `db5e23ae8c218808821327d806b05d2604cfadfb`, CI 41432038040 successful.
- 75 open PRs; 74 Draft and only #15 non-Draft. #15 explicitly targets learning/v1 and depends on Draft #9; do not merge out of order. No safely mergeable open PR was identified.
- Main advanced to `1afd8297e3c661bee3117ac5301b1ca08d64869b` at branch creation. Recheck against latest head after tests.

## Concrete P0 correctness defect and minimal fix
- `scripts/check_pr_evidence.py` called `tavern_ai.validate_receipt.validate`, which accepts duplicated values in the 8-seat `placements` list if all entries are 1..8. It does not enforce pinned game engine, seed, policy or checkpoint provenance.
- Main already has `tavern_ai.receipt_integrity.validate_integrity` implementing permutation, seed, pinned engine, policy and hash checks.
- This branch replaces only the PR gate import/call to use that existing stricter validator rather than creating another validator.
- Added independent synthetic-only regression tests; synthetic inputs are **not** game evidence.

## P1 model and training gate
- Current main has `models/registry.json` and strict checkpoint preflight tools, with a 1,408-step V5 Release candidate. It remains **unpromoted**, Champion null. Do not conflate a published ZIP with optimizer continuation verified from this exact Release.
- The shared `train.py` still supports MaskablePPO increments; changing it during concurrent model-resume PR work would overlap multiple sessions, so this round intentionally does not alter the trainer.
- **PPO gradient steps performed by this session: 0**. No candidate upgraded or archived in this branch.

## P2 rank-eight evidence audit (existing real runs, no new model assertion)
- Main evidence report `reports/s-20261102-83d91476/001-buy-opportunity-report.json` references authentic workflow 41428098018: V2 model rank [8,8], 0 actual Buy in 74 legal-Buy decision exposures, actions 1/2 = 222/248, 0 guard-forced ends. Matched baseline rank [6,7], 33 Buys in 48 legal exposures.
- Pinned upstream `crates/taverngym/src/actions.rs` at `fb61201a557ddd36a411cf44aac51ce4d9b606ce`: raw action 1 = Refresh, 2 = Freeze, 8..15 = Buy.
- Additional Draft PR #107 has authentic 3-seed ablation: forcing 46 purchases changed no rank (all 8) and increased guard-forced EndTurns. This rejects the simplistic hypothesis that adding any legal Buy is sufficient.
- Preliminary explanation: poor economic choices and low-value action loops; **causal training defect not established**. Investigate public-state deltas and Play↔Cancel loops before scaling.
- No official ranked TavernArena games. No new model games or policy-strength claims in this round.

## Independent verification state
- Branch-specific workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41449889626; task creates one genuine pinned-engine eight-seat baseline receipt, seed 801231, controlled seat 0. It is real only if run completes and strict receipt validation succeeds.
- Workflow artifact is temporary; upon success copy its genuine result into `experiments/s-20261102-dfa88e31/` with source run reference. Do not invent the receipt.
- PR final-head CI must run both regression tests and another genuine eight-seat full match before readiness.
- No safe merge until latest CI, full-match evidence and concurrency check pass.
