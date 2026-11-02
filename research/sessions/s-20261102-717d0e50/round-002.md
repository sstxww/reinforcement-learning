# Round 002 — Public-shop quality-aware Freeze vs blind Freeze

## One hypothesis
The negative R001 ten-pair test found unconditional late low-resource Freeze 7.7 mean rank vs original baseline 6.9. This new round tests whether a public shop quality gate prevents preserving low-value cards, improving rank. It uses the pinned engine and fresh independent seeds.

## Prior evidence and conflicts
Read main project/closed-loop/session protocols, R001 report and PR #40, main knowledge incidents, current open PRs. Concurrent work includes PPO loop guards, reward shaping, architecture, upgrades, refresh and sell. Only session-specific source/test/workflow/research were changed on a new branch created directly from main.

## Method and source
SESSION_ID: s-20261102-717d0e50. Round 2 branch agent/s-20261102-717d0e50/optimization-002. Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
Experimental source and fixed tests SHA: 5610b37eec2f0fa3b2926bdc5b49b232ce9c5dac.
Evidence commit SHA: 2b9ff6345b956d122d2653fd8821b995d6fb199e.
Upstream pinned commit fb61201a557ddd36a411cf44aac51ce4d9b606ce; observe2 patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
Actual TavernGym 1.1.0 source hash 6d8712c93022ba11, V2 4017 floats/447 cards, mask 245. The upstream public legacy observation has 3227 floats/124 card slots. Shop decoder uses only the same player's public Game.observe(0), while Game.observe2(0) is validated on every turn; never reads hidden opponent data.
Shop value heuristic: if selected baseline action is EndTurn, turns 4..9, no available Buy/Refresh, mask-legal Freeze, not already frozen and not already frozen this turn, freeze only if offered minion tier >= max(2, hero tier-1) and attack+health>=5. Baseline and blind-Freeze control share all other choices.
Ten independent seeds 29201–29210. Three game arms per seed: original baseline, blind Freeze (R001 equivalent, independent fresh seed), quality-aware Freeze. One owned seat 0 vs seven genuine Game.bot_play seats; run to Game.is_over with 30,000 loop protection and no fabricated fallback.

## Errors and corrective work
- First failure: https://github.com/sstxww/reinforcement-learning/actions/runs/41416920871; start-time assertion confused OBS_FLOATS=3227 old V1 with OBS2_FLOATS=4017. Unit tests and engine install had passed, zero games executed.
- Source fix ea4d436c3131419328f75faa481846caecc802fc: verify both versions; read public legacy V1 only for documented shop offsets; verify V2 for 4017/447 and all legal masks.
- Second failure: https://github.com/sstxww/reinforcement-learning/actions/runs/41417550965; 1/21 regression tests failed because new contract test used synthetic 60/19/28 sizing instead of actual 53/31/40, giving erroneous shop offset 488 vs 685. No simulator games.
- Test correction 5610b37eec2f0fa3b2926bdc5b49b232ce9c5dac; new regression checks both layout formats; no safety restriction removed.
- Final successful test and genuine 30-game action: https://github.com/sstxww/reinforcement-learning/actions/runs/41417682184. Unit tests, pinned engine, full games, receipt validation, evidence commit, temporary artifact all succeeded.
Detailed real failure evidence: failures/002-dual-observation-layout.md.

## Completed independent evaluation
| Policy | n | Mean rank (lower better) | Top4 | First | Freeze actions | Total seat-0 decisions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 10 | 6.8 | 1/10 | 0/10 | 0 | 553 |
| Blind Freeze | 10 | 7.1 | 0/10 | 0/10 | 44 | 625 |
| Quality Freeze | 10 | 7.2 | 0/10 | 0/10 | 32 | 600 |

Quality candidate minus baseline ranks: [0,0,4,1,0,1,-1,0,0,-1], mean +0.4. Quality minus blind ranks: [0,-2,2,0,0,1,0,0,0,0], mean +0.1. All candidates top-four 0/10. Quality gate reduces Freeze count but neither improves mean rank nor win/top-four rate in this 10-seed pilot. The difference is small and uncertain, with no statistical strength inference. **Do not promote**.

Every game received a genuine validated receipt in experiments/s-20261102-717d0e50/: quality "002-<seed>.json", blind "blind2-<seed>.json", control "control2-<seed>.json".
One mandatory own candidate game: seed 29201, 15 turns, 40 seat-0 decisions, rank 8, placements [8,3,1,4,5,6,7,2], freeze_actions 4, Game.is_over true; no illegal actions, combat truncation, or turn-limit ending.
Machine metrics research/sessions/s-20261102-717d0e50/metrics-002.json.

## Training and checkpoint
Pure strategy ablation: **zero PPO steps**, no model weights, model SHA256 not applicable, no checkpoint and no Best/Latest promotion. Artifact 13128082762 expires 2026-12-02 09:06:32 UTC; lightweight JSON receipts and metrics are committed in this unique branch.

## Next round hypothesis
Conditional Freeze did not reverse negative pilot. Shift resources to stronger policy selection/early-game board building rather than adding more Freeze heuristics to the shared baseline. Any next hypothesis needs independent seeds and at least one real completed game, with no overlap to concurrently open PRs.
