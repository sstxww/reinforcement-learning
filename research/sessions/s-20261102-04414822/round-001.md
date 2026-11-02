# Round 001 — planned card-embedding ablation

- Session: `s-20261102-04414822`
- Branch: `agent/s-20261102-04414822/optimization-001`
- Main base: `6ac59235b8238196a0e6462de77b72413c829372`
- Hypothesis: increasing card embedding width from 8 to 16 may change initial MaskablePPO outcomes; verify masks and compare matched seeds.
- Non-overlap: open PR #6 baseline, #7 evaluation, #8 infrastructure, #9 trainer; modify only `tavern_ai/model.py`, dedicated card-ablation runner/test/workflow.
- Real training, match and final statistics: **not executed at initial commit**. Workflow will replace this document only with real results.
- Evaluation: two matched seeds and 128 PPO steps per variant; too few to support superiority.
- Checkpoint: expiring per-session Action artifact only, no permanent checkpoint.
