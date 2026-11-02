# Round 001 — integration and paired evidence gates

- Session: s-20261102-30fe4978.
- Base main SHA: db5e23ae8c218808821327d806b05d2604cfadfb.
- Scope: additive fail-closed pair-audit CLI, unit tests, isolated bounded Actions workflow; no weights, reward changes or broad PPO training.
- Inventory at initial inspection: 75 open PRs, 74 draft; only non-draft #15 remains stacked on draft #9, so #15 is **not** an independent safe merge candidate. Main CI at run 41432038040 succeeded.
- Registry latest: V5 1408-step unpromoted Release v5-s-20261102-68099929-1408-41428692617; expected model digest a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632. Latest recorded three held-out placements [8,8,8], baseline [6,8,8]. No Champion.
- Separate confirmed V2 buy opportunity study: reports/s-20261102-83d91476/001-buy-opportunity-report.json, actual run 41428098018, two completed games seeds 45111/45112, 74 legal BUY action states, zero buys, 222/248 model actions were IDs 1 or 2. Guard intervened zero times in those observations. Do not infer that each BUY was strategically optimal or that repeated IDs were state-identical.
- Change: reject mixed model hashes, mismatched evaluation seeds, guarded policy labels, nonzero fallback, incomplete games, unpinned engine metadata, wrong controlled seat and non-permutation ranks before calculating paired means. Report n and descriptive approximate t CI, explicitly never auto-promote.
- Offline unit tests on newly authored isolated module: 12 passed; GitHub CI and independent full-game still required for review.
- Next: read actual isolated workflow result; save receipt/report in this session if successful. Diagnose raw IDs 1/2 against pinned TavernGym and observe actual state deltas; do not scale PPO while buy-action collapse remains.
- New PPO steps in this round: 0. New complete games in this round at branch creation: 0. Current candidate remains unpromoted.
