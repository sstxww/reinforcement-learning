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
Verified using completed GitHub Actions run https://github.com/sstxww/reinforcement-learning/actions/runs/41421935030 ; source commit 07c79259779499f3436b8cf8058769c4050fe7e6. Full test flow succeeded: initial pytest, pinned engine installation/hash, real-engine pytest, and six additional metamorphic cases across seeds 83011/83012. Hidden seat-1 hand and unobserved board stat perturbations preserved all bytes of seat-0 features/cards/mask in 4/4 cases; own seat-0 hand perturbations visibly changed features in both 2/2 positive controls. Total 6/6 passed. The probe's recorded SHA256s and limitations are in reports/s-20261102-42875425/001-observation-privacy.json.

Verified full game: baseline seat 0 vs seven simulator bots, seed 83031, 16 turns, 49 decisions, rank 8 (placements [8,7,1,3,5,6,4,2]), Game.is_over true, no truncated combats, no turn-limit termination. See experiments/s-20261102-42875425/001-83031.json. Not a learned policy or competitive gain. Training steps 0, no checkpoint.

Status: ENGINEERING_VALIDATED_REVIEW. No global privacy proof, no model promotion, no improvement claim. The one-shot workflow is retained as a manual dispatch after this run to avoid repeated push-triggered Actions on report/document changes.
