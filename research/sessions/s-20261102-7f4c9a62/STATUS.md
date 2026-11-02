# AutoTavern-AI independent session status

- SESSION_ID: s-20261102-7f4c9a62
- Current branch: agent/s-20261102-7f4c9a62/optimization-001
- Base main SHA: 6ac59235b8238196a0e6462de77b72413c829372
- Code experiment commit: e4af555a2f6687765988b4d2ae7a118a728ba1f3
- Genuine results commit: 23f3b298ababea09c294b31a101a43f56b6f3534
- PR to main: https://github.com/sstxww/reinforcement-learning/pull/16 (draft, reviewer/CI validation pending).
- Workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41413477918 (success).
- Completed real PPO steps: 256 total; 128 per entropy configuration. Independent training seed 70141.
- Mandatory completed full match: experiments/s-20261102-7f4c9a62/001-31041.json, agent seat 0 rank 8, 153 decisions, seed 31041, no guard truncation.
- Evaluation: 2 held-out seeds per arm. Mean rank original baseline 7.0; PPO entropy 0.0 8.0; PPO entropy 0.02 8.0; top4 0/2 in every arm. No demonstrated improvement.
- Best supported performance claim: one validated complete match and two paired seed evaluation per arm, NOT competitive strength.
- Model storage: GitHub Actions Artifact entropy-s-20261102-7f4c9a62-41413477918, run 41413477918, 30-day retention expiring 2026-12-02 UTC; no permanent checkpoint.
- Checkpoint paths within Artifact: checkpoints/s-20261102-7f4c9a62/{zero,regularized}/model.zip and model.metadata.json.
- SHA256 zero: 6c0f145d1e96cc878ebc729d59567e90a44548deacfcac53c82827a8e94d2ae1.
- SHA256 regularized: a31b0098abc1f285a7aa11b9ada9c827c9d2ba319666f60324a7153315ca6d9f.
- Restore: download the exact Artifact from run URL; compare each SHA256; install engine version 1.1.0, source hash 6d8712c93022ba11; load with sb3_contrib.MaskablePPO.load(...,device="cpu"). Permanent checkpoint persistence not implemented.
- Compact results: reports/s-20261102-7f4c9a62/entropy-comparison.json.
- Next: PR CI review, then >=2048-step, >=20-paired-game follow-up before claiming a preference for an entropy coefficient.
