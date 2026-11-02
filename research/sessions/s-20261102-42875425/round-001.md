# R001 — Pinned observe2 hidden-state noninterference

SESSION_ID: s-20261102-42875425
Branch: agent/s-20261102-42875425/optimization-001
Base main commit: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
State at initial creation: RUN_PENDING, live evidence not yet available.

## Hypothesis
A deployed policy must read only seat-0 observe2 float/card arrays and the legal-action mask. Perturbing stats of an opponent's unseen hand or precombat board minion — with constant card ID, hand/board counts and all other fields — should NOT change these input bytes. Editing our own hand minion must change our observations (positive control).

## Distinctness
This experiment does not change the PPO or behavior-cloning algorithms being tested in other branches. It adds only unique privacy probe source, unit/engine tests, workflow, and session outputs. No shared trainer, baseline policy, checkpoint, main branch, upstream or other session file is touched. Other sessions' draft PRs are preliminary leads only.

## Simulator provenance
Pinned upstream commit fb61201a557ddd36a411cf44aac51ce4d9b606ce; version 1.1.0, patched source hash 6d8712c93022ba11; patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0. Observation: 4017 float32, 447 int32 card IDs, 245 legal actions. Upstream actions.rs/obs.rs/debug.rs were checked for encoding, opponent visibility, debug fixtures and state restore semantics.

## Evidence plan
1. On isolated branch, bounded GitHub workflow runs unit pytest, installs pinned engine and runs engine-backed privacy tests.
2. Execute two new fixed-seed metamorphic probe states, 83011 and 83012. Save report to reports/s-20261102-42875425/001-observation-privacy.json.
3. Execute genuinely complete eight-player BASELINE infrastructure canary seed 83031 to Game.is_over(), save experiments/s-20261102-42875425/001-83031.json and run receipt validator.
4. Save actual workflow URL, results and limitations after it finishes. No training: PPO updates 0, BC updates 0; no checkpoint and no model promotion.
5. This is a narrow noninterference test, NOT proof of global non-leakage or competitive advantage. Gameplay metric for the control canary is only a single baseline placement, no paired superiority claim.

## Initial audit
Main has baseline and masked PPO with seeded full-game evaluation. GitHub releases exist, but a verified high-level champion is not established. Numerous competing draft PRs cover policy action priority, PPO hyperparameters, BC and seat effects. Earlier full-game model loop failures and release 403 are documented in CLOSED_LOOP.md.

## Live results
Pending bounded workflow; no successful test or full-game claim yet.
