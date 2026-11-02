# Round 002 — test hero-selection contribution

- Session: `s-20261102-b34940b0`, branch `agent/s-20261102-b34940b0/optimization-002`, starting main SHA `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Derived from verified negative [round 001 experiment #41415645714](https://github.com/sstxww/reinforcement-learning/actions/runs/41415645714), where global last `Choose` slot gave 4/4 rank 8 vs control [4,8,6,5].
- Upstream `flow.rs` directly shows `Game::new` initializes `turn=0` and `Phase::HeroSelect`; upstream `actions.rs` establishes generic `Choose` range 30–45.
- Hypothesis: preserving `turn=0` hero choice mitigates the negative global last-slot effect.
- Three policies: original baseline; last-slot in all phases; preserve original choices on turn 0 but last-slot for turn>=1. Shared baseline `tavern_ai/baseline.py` unmodified.
- Plan: 4 previous seeds 65201–65204 for direct reproduction plus 4 fresh held-out seeds 65301–65304; 24 real complete eight-seat simulated games, candidate slot 0, 7 official bots.
- Code/test/workflow: unique `choice_after_hero_s_b34940b0`; pending runtime evidence, no fabricated outcomes.
- PPO training: 0 steps, no neural model/checkpoint. Rule-policy config and SHA available once committed; engine TavernGym 1.1.0 source hash `6d8712c93022ba11`.
- Key caveat: turn-0 versus subsequent turn distinction does not isolate all choice types (targets, Discover, trinkets); paired results descriptive only.
