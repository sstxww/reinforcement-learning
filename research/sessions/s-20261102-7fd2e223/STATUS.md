# STATUS · s-20261102-7fd2e223

- Session: `s-20261102-7fd2e223`
- Round: 001
- Status: **verified full-game evidence, draft PR under independent CI review; hypothesis not confirmed**
- Branch: `agent/s-20261102-7fd2e223/optimization-001`
- Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- PR: https://github.com/sstxww/reinforcement-learning/pull/36
- Source: `tavern_ai/hero_power_probe_7fd2e223.py`, regression tests `tests/test_hero_power_probe_7fd2e223.py`
- Engine: genuine pinned TavernGym 1.1.0 / `6d8712c93022ba11`; 4017/447/245 contract.
- First run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415621730 — success, 22 unit tests, four candidate + four baseline complete eight-seat games.
- Heldout run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415938774 — success, 22 unit tests, eight new candidate + eight new baseline complete eight-seat games.
- Honest result: pilot candidate better by 2.0 mean ranks, but heldout candidate worse by 0.125; no demonstrated generalizable improvement. Combined n=12 paired, delta -0.583, candidate top-four 1/12 and first 0/12.
- Receipts: `experiments/s-20261102-7fd2e223/001-<seed>.json` and control receipts for seeds 73101–73112. Reports: `reports/s-20261102-7fd2e223/paired-001.json`, `paired-heldout-001.json`.
- Mandatory own game: seed 73101, candidate rank 4, actions 60, Game.is_over true, 0 illegal actions, 0 guard flags, engine match proof in run #41415621730.
- Training steps: 0 — this was a pure-strategy ablation, **not PPO training**.
- Model / optimizer checkpoint / SHA256: none. No persistent weights claimed. JSON evidence committed to Git, temporary 30-day artifact backups.
- Failure retries: 0. No session-specific failure signature to fix.
- Required next gate: review latest PR head CI, and preserve uncertain/negative evidence; **do not promote** to shared strategy.
