# Round 001 — isolated reward-scale experiment

- Session: `s-20261102-14ce98f3`
- Branch: `agent/s-20261102-14ce98f3/optimization-001`
- Immutable base main: `6ac59235b8238196a0e6462de77b72413c829372`
- Research focus: reward scale and MaskablePPO critic optimization, **not** a claim of competitive improvement.
- Hypothesis: scaling TavernGym rewards by 0.25 reduces critic value loss after 256 PPO steps compared with scale 1.0 under identical seed 74231. Any gameplay strength change remains unproven without more games.
- Existing knowledge reviewed: main README, AGENTS.md, docs/PROJECT_BACKGROUND.md, docs/SESSION_PROTOCOL.md, research/knowledge/README.md; main research/sessions/ had only .gitkeep. Open PRs #6 strategy, #7 evaluation, #8 infrastructure, #9 learning are unmerged. This experiment adds only new dedicated files to avoid their module edits.
- Engine: TavernGym 1.1.0, upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`, source hash `6d8712c93022ba11`, observe2 4017 float + 447 card + 245 legal-masked actions.
- Implementation: `tavern_ai/reward_study.py`, `tests/test_reward_study.py`, isolated cloud workflow `.github/workflows/reward-s-20261102-14ce98f3.yml`; no shared train.yml edits.
- Training planned: 256 PPO steps per arm, MaskablePPO with n_steps=128, 4 epochs, batch=64, learning_rate=3e-4, seed=74231, CPU. Total 512 attempted steps. Max 85 min per workflow.
- Full matches planned: baseline seed 26011, trained scaled and control models paired on seed 26012. Bot opponents from true patched TavernGym. All receipts must be from Game.is_over and pass validate_receipt.
- Actual training, CI, receipts, statistics and recovery: **PENDING remote execution**, never inferred from the workflow definition.
- Checkpoints: artifact `reward-models-s-20261102-14ce98f3`, 30-day expiry; NOT permanent until verified. Metadata includes SHA256 in metrics JSON after actual training.
- Comparison caveat: a single paired seed is not statistical proof of placement advantage. Next: add independent seeds, confirm receipt integrity and compare value-loss distributions across several training seeds.
