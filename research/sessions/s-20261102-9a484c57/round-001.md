# Round 001 — Scheduled tavern-upgrade before hand-play ablation

**Session:** `s-20261102-9a484c57`  
**Source branch:** `agent/s-20261102-9a484c57/optimization-001`  
**Base `main`:** `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`  
**Experimental source/fix commit:** `8f98639e13234ce65ecd69a3dfb2c427160e16d3`  
**Review:** https://github.com/sstxww/reinforcement-learning/pull/29  
**Successful real-engine run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415219995

## Hypothesis and isolation

The existing baseline handles mandatory discoveries, then plays held minions, then attempts scheduled tavern upgrades on turns `{2,5,7,9,11}` before routine buying. We hypothesized that prioritizing a **legal scheduled upgrade before a legal hand play** can improve eight-player placement. The initial mistaken phrasing about buy priority was corrected after reading the actual baseline and failing two test assertions.

No shared policy/model/trainer/evaluation files were touched. Files added: isolated `tavern_ai/upgrade_probe_9a484c57.py`, `tests/test_upgrade_probe_9a484c57.py`, own limited Actions workflow, session-only receipts/metrics and these research notes. Both arms use an equal 55-action-per-turn rescue budget; if action 0 is legal after budget exhaustion, they end the turn (no rescues actually occurred).

## Read-first shared evidence

Read main's `README.md`, `AGENTS.md`, `docs/{PROJECT_BACKGROUND,ARCHITECTURE,SESSION_PROTOCOL,CLOSED_LOOP}.md`, `research/knowledge/{README,INCIDENTS-20261102}.md`, and merged evaluation handoff. The open-PR scan found active work on MaskablePPO rewards, entropy, card inputs, purchase slot selection, play insertion and core economy; chose session-only code without editing those branches. Some unmerged PPO trials reported no strength gain, but their scores were not reused.

## Engine, safety, training and parameters

- Genuine patched TavernGym `1.1.0`, source fingerprint `6d8712c93022ba11`.
- Upstream pinned commit: `fb61201a557ddd36a411cf44aac51ce4d9b606ce`.
- Observe2 patch SHA256: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Features: 4017 float, 447 card indices, 245 legal-masked actions.
- Strategy code SHA256 from measured report: `2937953ab7d69330dc6fe810a4d60088fc88b5d74d61885c4c7d451e42d275be`.
- Strategy: mandatory action 30–45 first, scheduled legal upgrade action 3 before optional play, otherwise original deterministic `BaselinePolicy`.
- Candidate control: seat 0; opponents: seven TavernGym scripted bots; deterministic seeds `42021,42022,42023`.
- **PPO gradient steps: 0.** This was explicit rule-policy tuning; no neural checkpoint, optimizer state or model hash; Best/Candidate model registry unchanged.
- Real execution: `python -m tavern_ai.upgrade_probe_9a484c57 --seeds 42021 42022 42023`. Then `python -m tavern_ai.validate_receipt` on all six real JSON receipts.
- Dedicated workflow: `.github/workflows/experiment-s-20261102-9a484c57.yml`, bounded to 65 minutes, one session concurrency group, changes to receipt/report paths do not retrigger a push run. No Arena activity.

## Real full eight-seat game evidence

Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415219995 ; engine initialization, unit tests, 6 real full matches, receipt validation and GitHub evidence commit all passed.

| Seed | Baseline rank | Candidate rank | Candidate decisions | Candidate turns |
|---|---:|---:|---:|---:|
| 42021 | 7 | 7 | 63 | 16 |
| 42022 | 8 | 8 | 34 | 15 |
| 42023 | 8 | 8 | 62 | 15 |

- **Required own full game:** `experiments/s-20261102-9a484c57/001-42021.json`, seed 42021, candidate rank 7, 63 decisions, `placements=[7,8,5,1,6,3,4,2]`, `completed=true`, 16 turns, no truncated combat/turn-limit ending or illegal action.
- Additional candidate receipts: `early-upgrade-42022.json`, `early-upgrade-42023.json`.
- Baseline receipts: `baseline-42021.json`, `baseline-42022.json`, `baseline-42023.json`.
- All six: `Game.is_over()==True`, zero forced budget-ending actions, zero reported illegal actions.
- Compact machine-readable real data: `reports/s-20261102-9a484c57/upgrade-paired.json`; the original run code SHA is recorded in each receipt.

## Independent held-out paired evaluation

Three independent paired seeds; **six games** total, not six samples per arm.

| Metric | Baseline | Candidate |
|---|---:|---:|
| Mean placement | 7.6667 | 7.6667 |
| First-place rate | 0/3 (0%) | 0/3 (0%) |
| Top-four rate | 0/3 (0%) | 0/3 (0%) |
| Mean decisions | 53.0 | 53.0 |
| Forced endturn budget rescues | 0 | 0 |

Per-seed candidate-minus-baseline placement changes: `[0,0,0]`, mean `0.0`. Candidate policy recorded 10 scheduled priority-upgrade selections; baseline's zero for this *candidate-specific instrument* does **not** mean the baseline never upgraded. No direct counterfactual action-disagreement trace was collected, and identical rank/decision counts do not prove identical trajectories.

**Verdict: no observed placement gain; not enough evidence to infer a general strength difference. Do not promote this strategy or any Best model.**

## Failure, repair and follow-through

- First run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415062300 ; pytest 23 passed, 2 failed; genuine engine/game stage skipped.
- Root cause: incorrect test assumptions about original scheduled upgrade priority over buying, and about fallback when an upgrade had already been selected; the baseline code itself was behaving as written.
- Repair: https://github.com/sstxww/reinforcement-learning/commit/8f98639e13234ce65ecd69a3dfb2c427160e16d3 ; corrected expected actions with a legal hand-play alternative and narrowed the hypothesis. No tests were removed.
- Re-test: https://github.com/sstxww/reinforcement-learning/actions/runs/41415219995 ; unit tests and all six real complete matches passed.
- Dedicated failure record: `failures/001-baseline-action-order.md`.

## Recovery, retention and next experiment

All six JSON receipts and small summary were committed to this isolated branch; the run also uploaded a **30-day** Artifact backup, not permanent model persistence. Strategy code is recoverable via this branch. Since no PPO weights were trained, no checkpoint exists and no restore procedure is relevant.

**Next hypothesis:** augment the isolated probe with real decision-level counterfactual disagreement counts between original baseline and changed policy on the *same observed states*. Only if enough disagreements occur, perform a new held-out game comparison with a meaningfully distinct schedule. Avoid over-interpreting negative three-pair pilots or rerunning identical seeds without a new hypothesis. PR final-head CI must pass before review and integration.
