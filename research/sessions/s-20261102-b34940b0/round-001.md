# Round 001 — mandatory discover-slot bias

- Session: `s-20261102-b34940b0`.
- Hypothesis: when multiple legal forced choices are presented in action indices 30–45, taking the last option rather than the first may improve placement.
- Motivating evidence: main `BaselinePolicy` always takes first legal choice in [30,46); existing draft PRs focus on PPO, economy, buying, selling, board position, reward, and refresh. Overlap check performed 2026-11-02.
- Baseline main SHA: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Real experiment: four matched random seeds 65201–65204, seat 0 candidate/control vs 7 official TavernGym bots, full `Game.is_over()`, illegal-action guards and receipt validation.
- Changed files: private candidate implementation, tests, workflow and session-only research evidence. Shared baseline and training flow untouched.
- Learning steps: 0. This is a rules ablation, not a PPO experiment.
- Training config: none; environment pin TavernGym 1.1.0 / source fingerprint `6d8712c93022ba11`.
- Metrics / receipts / job URL / candidate policy SHA-256: pending actual run; do not infer values.
- Current outcome: experiment submitted for execution, not yet validated; no ranking improvement claim.
- Next hypothesis: if multi-option discovery opportunities exist but no gain, audit the selection's card-strength semantics instead of blindly choosing last.
