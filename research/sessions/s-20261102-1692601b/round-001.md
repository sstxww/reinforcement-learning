# R001 — publicly observable sell-and-buy optimization

- SESSION_ID: s-20261102-1692601b
- Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Branch: agent/s-20261102-1692601b/optimization-001
- Actual TavernGym target: 1.1.0, fingerprint 6d8712c93022ba11, observe2 4017/447/245.
- Historical findings: main's baseline never sells; upstream actions.rs defines Sell=16..22, Buy=8..15. Unmerged PRs address BC, PPO, freeze, refresh, upgrade, choice, but not this narrow sell-buy intervention.
- Hypothesis: with seven legal sells, no playable hand card, and an affordable shop buy, one late-game sale followed by immediate buy may improve completion/rank.
- Training/calibration: finite four-arm grid search (turn>=7/11 x sell slot first/last), training seeds 49131,49132; heldout seeds 59131..59134. 10 training games and up to 8 heldout games, with all receipts. Zero PPO/gradient steps and no new neural checkpoint, explicitly rule-parameter optimization.
- Inputs: only observed 245-bit mask, own public turn and action count. No opponent hands or future shops.
- Risk: lacks board-strength estimation. Sell-once cap cannot make a weak sell choice strategically useful. Record actual sales, follow-up buys, unpaired sales.
- Criteria: do not promote on 4 heldout seeds. If zero interventions, candidate is not a meaningful test. Any incomplete match blocks the experiment.
- Stage: code and bounded workflow submitted; REAL RESULTS PENDING.
