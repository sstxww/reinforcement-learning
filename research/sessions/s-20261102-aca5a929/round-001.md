# Round 001: Public-card purchase-target preference (independent session)

## Identity and provenance
- SESSION_ID: `s-20261102-aca5a929`
- Base: `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Branch: `agent/s-20261102-aca5a929/optimization-001`
- Upstream pinned TavernGym commit: `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, observe2 patch SHA256: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Engine source hash expected: `6d8712c93022ba11`; catalog SHA256 expected: `c4c42e6ce5060e1b79fbcd5f4edbf6d17495f0f52690072481d690610f7ef6d7`.
- No upstream, main, public Champion, other session, or Arena writes.

## Inherited evidence and conflict avoidance
- Read main AGENTS, architecture, background, session protocol, closed loop and historical incidents.
- Open PRs #61-64 attempt teacher imitation; other PRs study freeze, refresh, upgrade, hero power, seating and PPO. None is treated as validated/main.
- Primary known weakness: V0 Baseline always selects first legal shop buy (action 8–15); weights-only PPO can loop and has not established strong results.

## Mechanism and falsifiable hypothesis
- Upstream `crates/taverngym/src/actions.rs` encodes `Buy(shop slot i)` as `8+i` and masks unaffordable/illegal shop items.
- `crates/taverngym/src/obs.rs`: observable `cards` stream includes own board [19:26], hand [26:36], visible shop [36:44]; opponents' private cards are not used. Must reverify dynamically against `taverngym.layout()`.
- `taverngym.card_static()` maps card embedding index to minion kind, tier, base attack/health and race bits [15:26]. These are public static facts; game effects and unknown future cards are NOT predicted here.
- Hypothesis: replacing only **which legal minion shop slot to buy** based on public stats, tribe overlap and exact-pair count changes and potentially improves true eight-seat placements vs unchanged first-slot Baseline.
- Null: no improvement; this project is strategy selection, not full game understanding.

## Bounded optimization and validation
- Implemented unique `tavern_ai/card_synergy_aca5a929.py` and `tests/test_card_synergy_aca5a929.py`.
- Finite parameter candidates: (race,pair) = (0,0), (0.7,0), (1.8,0), (0.7,3.5); common stat=1.0, tier=0.5.
- Training seeds: 79110,79111, 2 complete eight-player matches per candidate (8 true games, 0 PPO/gradient steps); choose lowest training mean placement, tie -> first.
- Held-out comparison seeds: 79220–79223, baseline and frozen candidate on the same seeds (8 true games). Four pairs are **not** enough for strong improvement claim.
- Exact engine, action-mask legality, full completion, no truncation/turn-limit, guard-trigger count, buy-choice override count, checkpoint SHA256, separate training/heldout receipts recorded.
- Workflow: `.github/workflows/experiment-s-20261102-aca5a929.yml`; push paths restricted to own code/workflow, 75m limit, isolated concurrency group. Only own tiny checkpoint and receipt files committed. No auto-merge.
- Full reproducer after engine bootstrap: `python -m pytest tests/test_card_synergy_aca5a929.py`; `python -m tavern_ai.card_synergy_aca5a929 --run`.

## Execution status
This document is a **pre-execution** research protocol. Real trained weight SHA, game results, CI/run ID and PR will be filled only from a verified Actions run. NO results have been claimed here.

## Decision gate
RETEST if completion and comparison evidence exist but power is insufficient; REJECT for observed degradation; BLOCKED if real-engine execution cannot complete. No Champion upgrade from this n=4 pilot.

## Next hypothesis
If ranking changes buys but not placements, inspect action traces to test whether raw stats/tribe similarity correlate with midgame survival; compare stage-conditioned teacher labels, rather than increasing PPO steps.
