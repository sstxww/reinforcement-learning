# Round 001 — visible full-board replacement

Session s-20261102-cee57e6a. Base main commit 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.

Hypothesis: the stock baseline never sells minions, even if the seven-slot warband is full and a stronger minion sits visibly in hand. Test a one-per-turn board swap using only public observe2 data.

Pinned upstream actions.rs: Sell 16–22, Play 46–125, Magnetize 126–195. Pinned obs.rs: public board start 68 with 31 floats/minion, public hand start 285 with 40 floats/card. Runner checks these indices against actual own-game objects as test oracle; the policy itself receives only public features and mask, no opponents' hidden game data.

Bounded tuning: margin 4, 8 and 12; training seeds 73011 and 73012. Independently selected margin is tested at 73031–73033 plus mandatory canary seed 73029. All comparisons are against the unchanged V0 baseline and seven official game bots. 15 planned complete eight-seat matches, including 8 parameter-selection games. No PPO gradients or weight checkpoint. No Champion promotion based on small samples.

Evidence status: awaiting private workflow. Do not interpret this planned count as executed evidence.
