# Rules from pinned source — static facts vs experimental evidence

Only applies to TavernGym 1.1.0, upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce` with verified observe2 patch. Not verified commercial-client rules.

## Source-reviewed mechanics, not individually tested

- `crates/taverngym/src/config.rs::RulesConfig::default`: starting gold 3, +1 per turn, 10 refill cap; base buy 3, sell 1, refresh 1; base tier-up costs [5,7,8,11,11,10] and 1-per-turn discount; board 7, hand 10, normal max tavern tier 6. Actual prices can change via hero/card rules.
- `src/actions.rs::legal_mask`: pending choice restricts actions to Choose and possible Cancel; Buy legality uses actual slot price, health-cost allowance and hand capacity; Move excludes same-slot; spells only use hand-position zero.
- `src/recruit.rs::buy`: a `CAST_ON_BUY` spell may bypass full-hand restriction; GoldSpent and Bought events have explicit ordering. Not every purchase enters hand.
- `src/recruit.rs::freeze`: Freeze toggles current Tavern cards; already-all-frozen means unfreeze; press limits may apply.
- `src/recruit.rs::upgrade`: pays effective price and updates Tavern tier/next cost. Upgrade decisions cannot be hard-coded from turn number alone.
- `src/engine.rs::triple_need_of`: selected hero/trinket effects can reduce copies needed for a triple to two.
- `src/obs.rs`: opponent inputs are public summaries and last-seen combat boards, not hidden hand/live unseen board.

## Verified by real engine


## Real verified outcome — own GitHub Actions

- [Engine-backed workflow](https://github.com/sstxww/reinforcement-learning/actions/runs/41421685972) completed success against commit `90344e6a9149c89293194a7dc6417e98240fa203`.
- Tests: isolated 3/3 and full suite 20/20 passed. TavernGym 1.1.0, engine source hash `6d8712c93022ba11`, observations 4017 float/447 card, 245 masked actions.
- Full card catalog: 3,983 native static rows, 66 features each, sha256 `440fcd5f03efdce56efc49699a468f0f7cf5a4bd8f6282e9e3c2a6c8adcab654`. Source-only metadata: **not script effects**.
- Instrumented genuine eight-seat game seed 27861: baseline rank **1**, 54 decisions, 15 turns, completed without combat/turn guard truncation.
- Separate genuine canonical baseline receipt seed 27862: rank **7**, 41 decisions, 15 turns, placements `[7,5,1,6,3,4,2,8]`; real receipt validator passed.
- No new model, no training steps, no competitive-strength gain established; two different seeds are not an A/B comparison. Not a Best-candidate PR.
- Artifact [13130745769](https://github.com/sstxww/reinforcement-learning/actions/runs/41421685972/artifacts/13130745769), 30-day expiry on 2026-12-02; full catalog artifact is not permanently stored.
- Next requirement: final PR CI full-match pass and review; no direct main merge.

## Unverified work for next round

Build deterministic engine-state tests for effective buy/upgrade prices, freeze toggling, triple exceptions, Discover/Cancel and full-hand cases; test Battlecry/Deathrattle/Start-of-combat with actual event/state transitions. Static printed tags are not labels for trigger correctness and do not prove model strategy quality.

Source: https://github.com/MCG-NJU/AutoTavern/tree/fb61201a557ddd36a411cf44aac51ce4d9b606ce/crates/taverngym/src
