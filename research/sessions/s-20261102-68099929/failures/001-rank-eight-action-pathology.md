# V5 rank-eight action-pathology root cause audit — evidence vs hypotheses

**Audit date:** 2026-11-02. **Status:** `behavioral_failure_confirmed_root_cause_not_yet_established`.

## Source and data reliability
This audit **reuses** authentic model-controlled eight-seat evidence created by **another independent session** in [PR #60](https://github.com/sstxww/reinforcement-learning/pull/60), not new games by the present session. Original run: [41418438337](https://github.com/sstxww/reinforcement-learning/actions/runs/41418438337), final PR-head CI [41419208295](https://github.com/sstxww/reinforcement-learning/actions/runs/41419208295). Raw immutable-branch files:
- `reports/s-20261102-24728f13/002-action-telemetry.json`
- `experiments/s-20261102-24728f13/002-42174.json` and same seed family 42175–42176, plus reference arm
- `research/sessions/s-20261102-24728f13/failures/002-action-utilization.md`

Pinned TavernGym 1.1.0 engine source hash `6d8712c93022ba11`; observation: 4017 floats, 447 card slots, 245 legal-masked actions. Candidate checkpoint SHA256 `802c65e7da2ba42e26e2f2efb55859b91428f1b792428031947484ce95f42f18`, reference SHA256 `8450905bdd1d78e6be68175f9943b16ac840fc9ce2882da4e32791ddb078ad0c`. The source states both checkpoints recovered and SHA checked from original Artifacts, which may expire 2026-12-02.

## Observed actual outcomes

| Metric | Low LR 1e-4 candidate | Reference 3e-4 |
| --- | --- | --- |
| Distinct matched heldout seeds | 42174, 42175, 42176 | same |
| Actual complete model games | 3 | 3 |
| Placement by game | 8,8,8 | 8,8,7 |
| Top-four / first-place | 0/3; 0/3 | 0/3; 0/3 |
| Total controlled actions | 36 | 875 |
| Buy-slot actions | **0** | 20 |
| Model-chosen END_TURN | **21** | 3 |
| Forced legal END_TURN | 0 | **21** |
| Maximum same-action streak | 2 | **40** |
| Illegal actions or combat truncations | 0 | 0 |

Candidate END_TURN preference and reference repeated/guarded actions are empirically observed. There is no demonstrated model gain or beneficial LR mechanism. Paired candidate-minus-reference rank difference `[0,0,+1]` (lower rank is better); descriptive n=3 is not adequate for causal inference.

## Critical unknowns; **do not** claim proof
1. Number of turns where BUY was **actually legal** and affordable for the candidate; absence of BUY actions alone cannot establish bad purchase preference.
2. Which observation gold/shop/board features were present **before** each END_TURN; pending-choice legal masks may correctly exclude purchases.
3. Meaning of reference "other_action" raw IDs; whether repeated actions changed public state and advanced future decisions.
4. Whether actions 8..15 were present in legal masks as expected, and whether observation/card embeddings were misencoded.
5. Train vs full-match distribution shifts, actual reward/advantage/entropy/KL or value loss. The source report does not establish these.

## Falsifiable diagnosis, experiment plan with stop condition
Instrument **one small set of fresh, matched full real games**, stable engine/model exact hashes, independent seeds and seats. At each policy decision log:
- current turn, gold, shop/hand/board counts and **exact legal BUY candidates**;
- END_TURN selected with legal BUY and adequate currency vs none;
- legal opportunity counts, chosen action family, model-choice vs fallback override;
- before/after own-public-observation hash plus gold/board changes to identify zero-progress loops;
- end-of-turn unspent gold, purchases, total board size/quality proxy, and survival rounds.

Pre-register measures `P(BUY | BUY legal and affordable)`, `P(END_TURN | BUY legal and affordable)`, number of repeated no-progress actions, and early-game own-board sizes vs rule baseline. If the model consistently refuses legal buys, trial one isolated **training-data/auxiliary-target** change (not dozens of reward knobs) and evaluate on heldout paired seeds; if masks omit legal buys, correct mask/encoding and regression-test before new PPO steps. If behavior remains collapsed, **do not expand training**, do not promote Champion.

## Integration and retention
This issue is a **research failure report only**; no fake current-session weights, game receipts, or training metrics. Existing final release inventory is experimental only; independent verified V2 restore is being tested by this session's isolated workflow, not asserted until run success. Source PR #60 is stacked on #51; integrate in dependency order or extract only non-conflicting diagnostic code after tests.
