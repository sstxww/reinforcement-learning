# s-20261102-73729553 — R001: Masked action-family behavior cloning

## A. Provenance
- Unique branch: agent/s-20261102-73729553/optimization-001; initial main SHA: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
- Upstream pinned commit: fb61201a557ddd36a411cf44aac51ce4d9b606ce plus verified observe2 patch; actual runtime TavernGym 1.1.0, hash 6d8712c93022ba11, feature/card/action dimensions 4017/447/245.
- Evidence: isolated Actions run https://github.com/sstxww/reinforcement-learning/actions/runs/41420333302 (SUCCESS, unit tests, engine, supervised training, true eight-seat matches, and receipt commit). Result commit: 5317dd6aaf3cbb41ce0fed87062ef039548acca4.
- Historical input: curated INCidents research/knowledge/INCIDENTS-20261102.md; unmerged diagnostic PR #60 (PPO sometimes never buys); PR #59 (seat results not robust). These are leads, not merged guarantees.

## B. Game mechanism and hypotheses
The pinned upstream actions.rs defines all 245 legal action positions in 14 families. Its legality mask checks pending choice, hand capacity, price, cast-on-buy, health-price exceptions and board limits, not simplistic gold>=3. Pinned obs.rs gives player-visible gold, shop/upgrade price, tavern tier, health, board/hand counts. No opponent hidden hands, future shops or engine RNG was accessed.
Hypothesis tested: a tiny supervised policy can learn *action family selection* from public observation and engine legal mask, before attempting stronger card strategy or PPO. Teacher is the repository's weak deterministic BaselinePolicy; it is not expert gameplay.

## C. Algorithm and training
- New tavern_ai/bc_probe_73729553.py and tests/test_bc_probe_73729553.py; branch-isolated .github/workflows/bc-probe-s-20261102-73729553.yml.
- 39 public/mask/own-action-count inputs to 14 masked action-family logits; first legal action of family, no hidden-state access. Linear masked cross-entropy, 250 full-batch gradient updates, deterministic initial seed 73729553. Actual PPO steps: 0.
- Training dataset: 3 genuine complete teacher games, seeds 67010, 67011, 67012; 129 seat-0 teacher decisions. Training exact family accuracy 124/129 = 96.12%.
- Disjoint held-out teacher trajectories: seeds 67020, 67021; 94 decisions, family accuracy 90/94 = 95.74%. These are teacher-on-trajectory metrics, not off-policy generalization evidence.

## D. True matches and separate game strength
- Runner executed 12 genuine eight-seat full games: 3 teacher-training + 2 heldout-teacher + 1 pure learned-BC canary + 6 independent paired games. The first five are summarized by sampling counts in run log, while seven canary/paired match receipts are committed in experiments/s-20261102-73729553. All were driven to Game.is_over(); receipt-backed seven games passed validation with 0 combat truncations and 0 turn-limit endings.
- Own mandatory BC canary seed 67029: rank 8, 64 decisions, 16 turns, 15 buys, 23 plays, 16 choices, 2 upgrades, 8 end-turns, zero extra BC guards, zero only-end-legal occurrences. Full placements: [8,1,6,7,5,3,4,2].
- Independent paired seeds 67030,67031,67032: baseline ranks [8,8,8], mean 8.0; learned BC ranks [7,8,8], mean 7.667. Both top-four 0%, first-place 0%. Difference -0.333 rank in 3 pairs, 1 improved / 2 ties: tiny, uncertain, NOT demonstrated competitive superiority. Baseline 85-action overrides and extra BC guards were zero in these games.
- Learned model acts legally by real engine mask and completes full game, but has no card semantics or strategic synergy; high teacher imitation accuracy says nothing about expert-level strategy.

## E. Checkpoint and reproducibility
- Small JSON policy weights: reports/s-20261102-73729553/001-checkpoint.json (persisted on own Git branch), SHA256 ef09f865cbff3fe4b8685df77636045f8886264376dfd6660ff9355591a31ee2.
- Metrics: reports/s-20261102-73729553/001-results.json. Results include source hash, seeds, updates, decisions, action-family counts and individual ranks. Real game receipts under experiments/s-20261102-73729553/.
- Reproduce after pinned engine install: python -m tavern_ai.bc_probe_73729553 --receipts-dir experiments/s-20261102-73729553 --report-dir reports/s-20261102-73729553. Full Python tests also pass in run. Direct checkpoint reload-and-replay from committed JSON was not independently tested; do not claim recovery proof beyond presence/sha of small raw weights. 30-day Actions Artifact is not durable; branch-tracked JSON remains reviewable unless branch removed.

## F. Integration decision and next hypothesis
Decision: RETEST for competitive comparison, no model promotion. This is a positive basic-imitation engineering signal and a small inconclusive real-game result, not Champion material. The evidence supports adding model category diagnostics but not integrating weak BC as the production policy.
Unmerged PRs #9/#15 have more PPO steps but no verified rank advantage; do not conflate training volume with strength. No public shared modules or other session files were modified; release upload and Arena not attempted.
Recommended R002: verify checkpoint reload exactly and train a stronger *public-information* buy-vs-end decision teacher using heldout seeds and actual buy counts. Avoid blind PPO scaling.
