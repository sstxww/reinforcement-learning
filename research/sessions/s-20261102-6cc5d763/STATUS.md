# Session status — s-20261102-6cc5d763

- Current state: **first real-engine experiment completed; no improvement demonstrated; awaiting final-head PR CI**.
- Branch: `agent/s-20261102-6cc5d763/optimization-001`, base main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Code commit: `d1eed5699186a265d8c704bb7eaea917dec29535`.
- Real evidence commit: `9331ea278846c82a65e2edeab9d899ee6c727ba4`.
- Executed Actions: https://github.com/sstxww/reinforcement-learning/actions/runs/41415018609, success.
- Actual PPO training steps: **0**, rule strategy ablation (no model produced).
- TavernGym engine 1.1.0 / source hash `6d8712c93022ba11`.
- Mandatory complete candidate game: seed 36501, rank 8, 45 moves, receipt `experiments/s-20261102-6cc5d763/001-36501.json`, truncated combats 0, turn limit false.
- Held-out paired seeds 36502–36504, baseline and candidate each 3 games, ranks [8,8,8] in both arms, top-four 0%.
- Intervention count: 0 in all four candidate games, therefore experiment fails to test causal effect of refreshing; **not a strength success or a demonstrated negative effect**.
- Full metrics: `reports/s-20261102-6cc5d763/comparison.json`. Complete receipt names `experiments/s-20261102-6cc5d763/*.json`.
- Candidate policy SHA256: `e2f8d2f8d23b56489eef9de8f86b815fc468dd914f256ac84ab02a9809f64c36`.
- No model checkpoint; Best / Latest unaffected. Artifact 13127905152 expires 2026-12-02, not permanent checkpoint storage.
- Failure analysis: `research/sessions/s-20261102-6cc5d763/failures/001-zero-activation.md`.
- PR: to be filed; no merge authorized.
- Proposed R002: one refresh before the first midgame buy when both choices legal, with explicit intervention counter and fresh seeds.
- No Arena games, no other branches touched.
