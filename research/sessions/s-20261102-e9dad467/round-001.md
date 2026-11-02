# Round 001: seat-rotation evaluation

- Session: s-20261102-e9dad467
- Branch: agent/s-20261102-e9dad467/optimization-001
- Main base: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Hypothesis: measuring only seat zero can obscure positional sensitivity in full-game baseline evaluation.
- Status: initial source and regression tests written; real engine experiment not yet verified when this note was created.
- Historical context: main includes completed seat-0 baseline evidence and CI; unresolved historical PPO step-limit and Release 403 are unrelated to this engineering task.
- Other concurrent work: PPO hyperparameters, reward shaping, upgrades, card embeddings, receipts, and choice actions; this experiment adds a separate seat-rotation module.
- Code: tavern_ai/seat_rotation.py and tests/test_seat_rotation.py, no modifications to public baseline, engine, train.yml, or shared model.
- Environment: pinned upstream fb61201a557ddd36a411cf44aac51ce4d9b606ce, TavernGym 1.1.0, observe2 4017/447/245; patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
- Experiment budget: 2 independent engine seeds (41021,41022), three controlled seats (0,3,6), six genuine complete games, max 30000 outer iterations per game, 70-minute job cap.
- Training: 0 PPO steps (engineering measurement, not model-training experiment).
- Policy: the existing deterministic baseline; model SHA256 not applicable; exact baseline source SHA256 is recorded in generated receipts.
- Baseline comparisons: seat 0 versus seats 3 and 6 at the same seeds, descriptive rates only. Seat changes can also alter hero/draw interactions; not an isolated causal effect.
- Artifacts: workflow will write experiments/s-20261102-e9dad467/*.json and reports/s-20261102-e9dad467/rotation.json only upon real game completion; do not claim evidence before it exists.
- Checkpoint: none; no training performed. No Best or Candidate promotion.
- Next round: rerun more held-out seeds and incorporate seat permutation into an independent PPO comparison only if engineering gate passes.
