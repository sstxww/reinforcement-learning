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

## GitHub Action verification (actual, completed)

- Isolated run https://github.com/sstxww/reinforcement-learning/actions/runs/41449782276 **success** at branch commit fbadc86707641b6757263296a1a9f40de4ca2584. Twelve isolated tests and retrospective 3-seed paired evidence gate succeeded. Run artifact 13143902652.
- This session's own authentic complete eight-seat pinned TavernGym baseline game seed 39711: rank 7; 54 decisions; 14 turns; zero truncated combats; no turn-limit end. Exact stdout receipt is now tracked at `experiments/s-20261102-30fe4978/001-39711.json`, not an invented/borrowed match.
- Paired pre-existing V5 candidate [8,8,8] vs baseline [6,8,8], candidate minus baseline deltas [2,0,0] and mean +0.6667 (larger rank is worse); descriptive approximate t 95% interval [-2.202, 3.535], zero included, no gain. Raw model/guard 0, no new trained weights or game matches beyond own baseline game. Source receipt pair is pre-existing, not falsely claimed as this session's model games.
- First PR CI 41449815958 had 245 passed / 1 skipped but failed project `check_pr_evidence.py` due to no branch-tracked independent receipt. Now adding the genuine Action-produced receipt to address that blocker; new CI required.

## Verified simulator action mapping for P2

From read-only pinned upstream `MCG-NJU/AutoTavern` commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, `crates/taverngym/src/actions.rs`: action 1 = Refresh and action 2 = Freeze, action 8+ = Buy; `crates/taverngym/src/recruit.rs`: Refresh can spend gold; Freeze toggles the current Tavern cards' freeze state and may be repeated when freeze cap allows. Source: https://github.com/MCG-NJU/AutoTavern/blob/fb61201a557ddd36a411cf44aac51ce4d9b606ce/crates/taverngym/src/actions.rs and https://github.com/MCG-NJU/AutoTavern/blob/fb61201a557ddd36a411cf44aac51ce4d9b606ce/crates/taverngym/src/recruit.rs. Existing V2 sample's 222/248 raw Refresh/Freeze actions with 0/74 legal BUY decisions therefore identify an *action-family collapse*, not a proof of fully unchanged states or unique root cause. Next test before tuning rewards: log freeze toggles, refresh costs, gold and board size per step, legal BUY mask, action logits and state-change fingerprints.
