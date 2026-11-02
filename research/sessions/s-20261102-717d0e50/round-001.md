# Round 001 — Low-resource Freeze-at-exit ablation

## Hypothesis and motivation
The main baseline never uses Tavern Freeze. Upstream TavernGym actions.rs confirms A_REFRESH=1, A_FREEZE=2, A_BUY=8. The candidate inserts at most one mask-legal Freeze before an otherwise intended EndTurn on turns 4..9 when Buy and Refresh are both illegal. The one-freeze-per-turn guard avoids toggle loops.

## Prior art and collision audit
Read README.md, AGENTS.md, docs/PROJECT_BACKGROUND.md, docs/ARCHITECTURE.md, docs/SESSION_PROTOCOL.md, docs/CLOSED_LOOP.md, research/knowledge/README.md and INCIDENTS-20261102.md; checked main commit, open PRs, latest Actions and previous model releases. Main research sessions/proposals held only .gitkeep; open PRs covered upgrade, refresh, purchase slot, sell, standing, PPO loop guards, entropy, reward shaping and card encoding. Kept all source changes in this session's unique runner/test/workflow and did not change shared baseline/train/evaluation.

## Provenance
- SESSION_ID: s-20261102-717d0e50; branch: agent/s-20261102-717d0e50/optimization-001
- Base main SHA: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Experiment source SHA: 665dcaddac099fbdd2788a37bb687f5fe5e4a501
- Real match data commit SHA: c26bdd0ed8e4a9e57f34ad414ba5c76692adc780
- Upstream pinned commit: fb61201a557ddd36a411cf44aac51ce4d9b606ce
- Observe2 patch SHA256: 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0
- Actual TavernGym engine 1.1.0, source hash 6d8712c93022ba11, 4017 float features, 447 card index slots, 245 masked actions, 3984 catalog cards.
- Engine full-game loop safety max 30000; baseline per-turn action cap 85; candidate never repeated Freeze in the same turn.
- Independent workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41415783527

## Real run, tests and receipts
The one triggered workflow succeeded. Pytest, pinned engine bootstrap, all 20 real eight-seat matches, receipt validation, session-owned evidence commit and artifact upload all succeeded. Seat 0 was controlled by the actual policy, seats 1..7 by official taverngym.game.bot_play. Complete games required Game.is_over() == True; zero illegal actions, combat truncations, or simulator turn-limit endings.

Paired seeds 29101 to 29110. Candidate receipts experiments/s-20261102-717d0e50/001-<seed>.json, control receipts experiments/s-20261102-717d0e50/control-<seed>.json. All 20 JSON receipts are committed.

Mandatory independent candidate game, seed 29101: turns 17, 41 seat-0 decisions, seat 0 rank 8, all placements [8,1,5,7,3,2,4,6], four Freeze actions, completed True, zero invalid actions/engine guards.

## Paired evaluation (rank 1 = best)
| Metric | Baseline | Candidate Freeze |
| --- | ---: | ---: |
| Games | 10 | 10 |
| Mean rank | 6.9 | 7.7 |
| Top-four | 1/10 | 0/10 |
| First | 1/10 | 0/10 |
| Total seat-0 decisions | 503 | 477 |
| Actual Freeze actions | 0 | 35 |
| Ranks | 7,1,8,7,8,8,8,7,7,8 | 8,8,8,8,8,8,7,8,6,8 |

Candidate minus baseline paired differences: [1,7,0,1,0,0,-1,1,-1,0], mean +0.8, sample stdev 2.2997584414. Candidate worse in 4 pairs, better in 2, tied in 4. Seed 29102 (control first, candidate last) contributes most of the mean gap. The negative pilot is **not a statistically confirmed population disadvantage** at n=10, and no competitive gain is established.

Machine-readable metrics: research/sessions/s-20261102-717d0e50/metrics-001.json.

## Training and checkpoint
This is a deterministic pure-strategy tuning experiment; **actual training steps: 0**. No PPO policy controlled these matches. There is no model checkpoint, no model hash, no Latest or Best promotion. The only artifact is a short-lived evidence ZIP (GitHub Actions ID 13128190086) expiring 2026-12-02. Receipts and metrics remain as Git commits in this independent branch.

## Failures and next round
No session-specific failures occurred; do not create fictitious failure files. The negative screening result should not be integrated into the shared policy. Other sessions' PPO action loops motivate strict per-turn action guards. The next hypothesis is a value-aware Freeze policy using only public observable shop data, tested on fresh held-out seeds before modifying shared code.
