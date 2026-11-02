# s-20261102-c6c2196f R001 — Eight-seat receipt integrity

## Research hypothesis
The shared `validate_receipt.validate()` accepts a duplicated placement vector because it checks each rank's range but not the full permutation. A separate, strict, independent validator will reject such evidence while accepting genuine TavernGym completed eight-seat matches.

## Baseline and provenance
- Base SHA: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Engine: pinned TavernGym 1.1.0, `observe2` 4017 float + 447 cards + 245 actions, source `6d8712c93022ba11`.
- Existing knowledge: `research/knowledge/INCIDENTS-20261102.md` notes model no-progress, release 403, action encoding 55/61, and concurrent workflow cancellation. Different scope; these are not assumed resolved.
- Other open PRs occupy PPO, embeddings, economy, positioning, infrastructure and evaluations. This work changes only new independent modules and session-named files.

## Planned isolated experiment — awaiting actual evidence
- Synthetic negative baseline: duplicated rank vector is accepted by the existing legacy validator. Run the assertion in CI.
- Unit regression: strict validator must reject negative mutations and accept structurally valid completed evidence.
- Actual games: three independent seeds `36001, 36002, 36003`, seat 0 original `BaselinePolicy`, seven TavernGym bots; all must pass `Game.is_over()` via existing canary and strict validator.
- Steps: **0 PPO steps** (engineering experiment, not model improvement).
- Run: dedicated GitHub Actions workflow `experiment-s-20261102-c6c2196f.yml`, at most 65 min, no shared training job.
- Receipts: `experiments/s-20261102-c6c2196f/001-*.json` generated only by genuine game execution.
- Metrics: `reports/s-20261102-c6c2196f/receipt-integrity.json`.
- Model checkpoint: none; cannot infer performance improvement.
- Run ID, actual rank/decision counts, test conclusion, PR, and failure details: **pending** until runner evidence exists.

## Next hypothesis
Investigate stronger receipt provenance against accidental model/baseline confusion only after completing and reviewing this round.
