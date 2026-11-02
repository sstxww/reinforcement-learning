# Round 002 — held-out genuine TavernGym seat-rotation replication

## Origin and hypothesis
- Session: s-20261102-e9dad467.
- Branch: agent/s-20261102-e9dad467/optimization-002.
- Main base: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
- Stacked on R001 commit baee34ae58555dfe7dc57725e958881abfc98f87 and PR https://github.com/sstxww/reinforcement-learning/pull/43 (R001 passed independent PR CI). R002 PR: https://github.com/sstxww/reinforcement-learning/pull/55 (draft; do not merge before R001).
- Hypothesis: whether the descriptive seat 3 rank-7 vs seat 0 rank-8 pattern of two early seeds remains under new held-out seeds.
- Prior learning: R001 real six-game run 41416644671, n=2 per seat, no top-four and no causal evidence. Other sessions are exploring PPO rewards, entropy, embeddings, purchase slots; this round only adds isolated receipts and testing.

## Code, setup and real evidence
- Initial R002 commit 894d071d4e86977cca711fecef28dc13a4022d2c: add --round CLI and stable per-round receipt names, regression test and new unique bounded Actions workflow.
- Real results commit ce81f60150d7699fc8dd208f15dab373e63d0bb9.
- Completed workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41417454842, **success**.
- Pytest: 16 tests passed; TavernGym wheel built and imported; source fingerprint verified.
- Engine: TavernGym 1.1.0, source 6d8712c93022ba11, pinned upstream fb61201a557ddd36a411cf44aac51ce4d9b606ce, patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0, observe2 4017/447/245.
- Policy: deterministic baseline source SHA256 e4722a44660f8a880c9eeb949c80e81ebb652926f43d71acd64f958762bd6bac, one controlled seat per match, seven official rules bots.
- Training: actual PPO steps **0** (engineering evaluation, not model study). No model checkpoint, Best promotion or claim of PPO improvement.
- Game budget: 4 independent seeds 41023–41026 × seats 0,3,6, 12 complete genuine games. Guard: max 30000 simulation loops per match, 70-minute Actions timeout. All 12 Game.is_over() true, zero truncated combats, zero turn-limit-end, and receipt agent_placement equals placements[seat].
- Receipts (all real engine outputs): experiments/s-20261102-e9dad467/002-41023.json through 002-41026.json and rotated-002-*seat3.json / *seat6.json.
- Metrics: reports/s-20261102-e9dad467/rotation-round002.json, 12 real games.
- R002 agent decision count sum across twelve games: 558.

## Held-out seed results

| Seed | Seat 0 | Seat 3 | Seat 6 |
| --- | ---: | ---: | ---: |
| 41023 | 8 | 7 | 8 |
| 41024 | 5 | 7 | 8 |
| 41025 | 6 | 7 | 8 |
| 41026 | 7 | 7 | 8 |

All R002 seeds: seat 0 mean rank 6.5 (n=4), seat 3 mean 7.0 (n=4), seat 6 mean 8.0 (n=4), each seat top4 0% and first-place 0%.

Combined R001+R002 **18 real games**:
- seat 0 ranks [8,8,8,5,6,7], mean 7.0, top4 0%, first 0%;
- seat 3 ranks [7,7,7,7,7,7], mean 7.0, top4 0%, first 0%;
- seat 6 ranks [8,8,8,8,8,8], mean 8.0, top4 0%, first 0%.
Overall mean rank 132/18 = 7.3333, first-place 0/18, top-four 0/18. Seeds 41021–41026; six games per seat.

## Outcome and limits
The R001 pattern (seat 3 better than seat 0) **did not replicate as a mean-rank advantage** on four new seeds. The baseline is demonstrably very weak in this sample, not improved. The persistent rank-8 for seat 6 is a descriptive pattern only: seat changes can affect hero allocation, RNG, shop draws and bot interactions; n=6 is inadequate for causal claims. There is no PPO checkpoint in this session, so these are baseline-only measurements, not model quality results.

## Reproducibility, durability and next
- Run: python -m tavern_ai.seat_rotation --agent-id s-20261102-e9dad467 --round 2 --seeds 41023 41024 41025 41026 --seats 0 3 6 --receipt-dir experiments/s-20261102-e9dad467 --report reports/s-20261102-e9dad467/rotation-round002.json
- R002 Artifact seat-rotation-r002-s-20261102-e9dad467 expires 2026-12-02; receipt JSON is committed in own branch; Artifact is not permanent training state.
- No failures occurred this round; no permission escalation or release attempted.
- Next hypothesis: eval across a larger balanced seat×seed×hero grid, and compare an actual candidate PPO or improved policy with baseline under identical seeded seat assignments. Do not infer improvement without enough independent games.
