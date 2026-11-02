# Mechanism audit 001 — TavernGym observable action contract

Session: `s-20261102-661adf61`; pinned upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`.

Provenance: upstream `docs/TAVERNGYM.md` at exact pinned commit and our `tavern_ai/contract.py`. This audit describes *implemented upstream interface semantics*, not superior strategic choices.

| Action indices | Pinned meaning |
| --- | --- |
| 0, 1, 2, 3 | End turn, Refresh, Freeze, Upgrade Tavern |
| 4–5 | Hero power target/slot |
| 6–7 | Dark Gift button / Back out |
| 8–15 | Buy Tavern card 0–7 |
| 16–22 | Sell warband minion 0–6 |
| 23–29 | Activate warband minion 0–6 |
| 30–45 | Pending choice option 0–15 |
| 46–125 | Play hand card 0–9 at board position 0–7 |
| 126–195 | Magnetize hand card 0–9 onto board minion 0–6 |
| 196–244 | Move board minion to board position |

The pinned Arena `observe2` contract is 4,017 float features, 447 card slots and 245 discrete actions, and each turn's actual legal mask must gate all outputs. The unpatched upstream docs refer to older 3,227/124 observation sizes, so these must not be mixed with our patched observe2. Prior PR #28 documents the important **126–195 means Magnetize, not Sell** correction.

Version-sensitive content: upstream `docs/CONTENT.md` reports 244 implemented tier-1-to-6 shop minions, 116 hero powers, 70 Tavern spells, 236 Trinkets and 47 Dark Gifts for the pinned content pack. These are registry coverage claims, not that every card's effects are strategically modeled correctly or that the external live client has the same rule version. Do not assume all official features are implemented.

## Tests and unverified tasks

- Mechanism correctness exercised directly by the experiment: inspect `observe2` and `legal_mask` for real seat-0 states, accept only legal teacher labels, and fail on malformed dimensions/empty mask.
- Python unit tests additionally verify that the network cannot select masked-out actions, and that guarded vs raw match metrics are separate.
- **Not yet demonstrated:** card-effect timing, triple/discover semantics, economy affordability edge cases, positioning expected-value comparison, true strategic synergy, and zero-guard model completion. These require separate real-engine test fixtures and held-out evaluations before any capability claim.

## Core failure hypotheses for this round

1. Teacher has an `actions_used` memory used to force End Turn after 85 actions, while the distilled neural policy is not given that counter; BC may therefore fail to learn termination behavior.
2. Many mechanically distinct choices share one 245-index categorical head; action legality alone cannot express card value or strategic opportunity costs.
3. The reference teacher is a weak deterministic baseline; even a perfect imitation cannot establish an improvement in mean placement.
