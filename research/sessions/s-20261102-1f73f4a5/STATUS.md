# s-20261102-1f73f4a5 — STATUS

- Branch: `agent/s-20261102-1f73f4a5/optimization-001`.
- Main base: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Draft PR: https://github.com/sstxww/reinforcement-learning/pull/61.
- Experiment run https://github.com/sstxww/reinforcement-learning/actions/runs/41420063194: **completed SUCCESS**; 4/4 newly added unit tests and real pinned-engine execution passed; 6 complete eight-seat games (2 teacher training, 2 teacher heldout, 2 guarded student heldout).
- 113 teacher train samples, 5 Adam updates; 88 heldout teacher decisions, exact agreement 63.64%, masked legality 100%.
- Teacher heldout ranks [8,6], guarded student [8,8]; forced ends [2,1]; no advancement.
- Model hash: `7be2f5b2a7b2778ce5f3a2a7c0ca4d5c8f79fa0d15e16d83a5ee0e4c71eec669`.
- Checkpoint: GitHub Actions artifact ID 13129372107, name `bc-s-20261102-1f73f4a5-model`; scheduled expiration 2026-12-02; NOT persistent. Artifact contains student.pt and real JSON evidence. Last model is NOT Best.
- Real receipt paths: `experiments/s-20261102-1f73f4a5/*.json` on this branch.
- CI #41420340906 initially lacked evidence; CI #41420778736 (21 unit tests passed) rejected a non-receipt summary.json in root. Report moved to reports/summary.json with source/workflow regression fix; final CI remains pending. See `failures/001-evidence-gate.md`.
- Model promotion: **REJECT** (negative 2-seed pilot; no raw student completion proof).
- Restore: download run artifact while retained; verify SHA256; check `tavern_ai.contract.verify_engine()` fingerprint, rebuild architecture `build_model(3984)`, load `student.pt` with `torch.load(weights_only=True)`; never silently use different card mapping.
- Next candidate: improve quality/breadth of teacher actions and add phase/economy progress labels before longer RL; fully revalidate no-guard policy.

## Repaired rerun / recovery
- Bounded rerun https://github.com/sstxww/reinforcement-learning/actions/runs/41421070436: SUCCESS. Metric layout fix confirmed, results/model SHA reproduce exactly.
- Latest receipt commit `786e86280bb601c519c657a3ea1264eff988cb11`; recent artifact ID 13130276501 expires 2026-12-02T09:32:23Z. Raw unguarded student not evaluated; guarded results negative. Distinct heldout seeds n=2 only.
- PR CI https://github.com/sstxww/reinforcement-learning/actions/runs/41421152840: **SUCCESS**, 23 unit tests, 4 valid match receipts and full CI eight-seat game.
- Next step: integrator review as negative BC pilot; do not merge as performance improvement. Research recommendation is to port/verify stronger observable teacher or add action-progress labels.
