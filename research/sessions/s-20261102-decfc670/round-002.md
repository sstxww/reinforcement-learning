# Round 002 — measured real-model rank-eight action utilization

Session `s-20261102-decfc670`, independent branch `agent/s-20261102-decfc670/optimization-001`, base main `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`. Pending integration Draft [PR #95](https://github.com/sstxww/reinforcement-learning/pull/95).

## Exact environment and checkpoint

- TavernGym 1.1.0 source fingerprint `6d8712c93022ba11`, pinned upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, observe2 4017 float +447 card +245 discrete masked actions.
- V2 released MaskablePPO: `v2-learning-41413557445`, 1280 reported steps; **independently downloaded and SHA256 verified** `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a` by [success run #41427457452](https://github.com/sstxww/reinforcement-learning/actions/runs/41427457452). It loaded on CPU and took one legal masked initial action. At that stage resume/full model game/Champion checks were false.
- Independent [diagnostic run #41428096980](https://github.com/sstxww/reinforcement-learning/actions/runs/41428096980) completed **SUCCESS**, repository pytest, pinned engine, checksum/load, *two real full eight-seat model-controlled games* (not baseline fallback) and branch-owned receipt persistence.
- Controlled model actions were legally masked. After 40 intra-turn decisions the diagnostic could force action 0 END_TURN for safety; every such forced action is recorded, so these are **guarded-model** games, not unguarded model-strength proof.
- Model training steps in this round: **0**; no new weights.

## Exact heldout measurements (new seeds, no tuning)

| Seed | Controlled rank | Total decisions | Actual Buy (8–15) | States with legal Buy | Model END when Buy legal | Model END total | Forced END | Observation+action exact repeats |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 86251 | 8 | 122 | 0 | 39 | 0 | 7 | 0 | 0 |
| 86252 | 8 | 164 | 0 | 38 | 0 | 5 | 2 | 0 |
| **Total** | **8,8** | **286** | **0** | **77** | **0** | **12** | **2** | **0** |

Raw live receipts: `experiments/s-20261102-decfc670/002-86251.json`, `002-86252.json`. Compact metrics: `reports/s-20261102-decfc670/002-rank8-opportunities.json`.

Both games had `completed=true`, eight valid placements, `truncated_combats=0` and `turn_limit_end=false`. Model actions grouped as `other`: **114+151=265 of 286**, versus 0 Buy. This is *not* proof that 265 actions were invalid or nonprogress: exact same observation+action repeats were zero, and the category needs deeper raw-ID decode.

## Root cause status

**Reproduced symptom:** this checkpoint never purchased a shop minion despite 77 decision points where at least one Buy action was legal. Given masks from actual `Game.legal_mask(0)`, this strongly motivates investigating severe purchase under-utilization. It does **not** prove optimality/affordability, long-term strategy pathology, or that skipping every such purchase was itself the cause of 8th place.

**Rejected premature conclusion:** on these seeds, `model_ends_with_legal_buy=0`; therefore “always prematurely END_TURN instead of buying” is NOT directly supported for this checkpoint. This differs from earlier PR #60's *different* low-LR model, which voluntarily ended 21/36 decisions while never buying on n=3; do not conflate checkpoints or training regimes.

Next falsifiable test: decode the 265 `other` action IDs and actual economy effect; compare value-aware Buy opportunity policy in fixed checkpoint on fresh paired seeds. Do not promote a blind first-legal-buy override without candidate and reference full-game tests. Existing model remains challenger, not Champion.

## Storage and safety

This round created no new weight. V2 immutable Release exists separately from 30/90-day Artifacts. Logged exact source SHA, seeds, two authentic receipt paths and independent run. No official Arena games, no upstream writes, no hidden opponent state consumed by policy.
