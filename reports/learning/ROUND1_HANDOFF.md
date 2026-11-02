# Round 1 learning handoff (2026-11-02)

Branch: `agent/learning/v1`; PR: https://github.com/sstxww/reinforcement-learning/pull/9

Verified genuine 256-step MaskablePPO training in https://github.com/sstxww/reinforcement-learning/actions/runs/41412362662. Engine TavernGym 1.1.0, source hash `6d8712c93022ba11` and observe2 4017/447/245. Training seed 42.

Model-controlled full eight-seat receipt: `experiments/learning/v1-model-match.json`, seed 1302, 13 turns, 149 controlled decisions, placements `[8,3,4,6,5,2,1,7]`. Earlier branch baseline smoke game: `experiments/learning/seed-12001-3df8b8f1aadb.json` seed 12001, seat-0 rank 8.

Held-out 3 games at seeds 24000–24002: ranks `[8,8,8]`, average rank 8.0, 0% top four, 0% wins. No proven performance gain. Candidate weights (not Best): https://github.com/sstxww/reinforcement-learning/releases/tag/v1-learning-9eada5801f99 ; SHA-256 `dc5195658995358e70c0d565a979b9cf05ccc5e47ae7adaa0a2f078f01cad917`. Files `model.zip`, `model.metadata.json`, `v1-heldout.json` are Release assets; full-game receipt remains committed to branch. Explicit standalone checkpoint restoration test and current-head PR CI remain separate validation steps.

Next: robust model/action budget, paired seeded baseline, reward ablations, resume test, no auto-promotion.
