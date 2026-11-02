# AutoTavern-AI V2 — session s-20261102-9a484c57

- **Research state:** `completed_for_review` for Round 001 (strength improvement **not** demonstrated).
- **Branch:** `agent/s-20261102-9a484c57/optimization-001`.
- **Main base SHA:** `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- **Experiment logic commit:** `8f98639e13234ce65ecd69a3dfb2c427160e16d3`.
- **PR:** https://github.com/sstxww/reinforcement-learning/pull/29 (draft; integrator review required; check final-head PR CI status).
- **Dedicated execution:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415219995 — success, actual TavernGym bootstrap, unit tests, six genuine complete games, receipts validated and committed.
- **First failure:** https://github.com/sstxww/reinforcement-learning/actions/runs/41415062300 (two incorrect priority assertions); fixed and separately documented in `failures/001-baseline-action-order.md`.
- **Training:** zero PPO steps; rule-policy ablation only, no checkpoint or trained model. Model SHA256: N/A. No Best promotion.
- **Engine:** TavernGym 1.1.0 / hash `6d8712c93022ba11`; upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, observe2 patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`, 4017/447/245 contract.
- **Strategy SHA256:** `2937953ab7d69330dc6fe810a4d60088fc88b5d74d61885c4c7d451e42d275be`.
- **Mandatory own match:** `experiments/s-20261102-9a484c57/001-42021.json` — completed true, rank 7, 63 actions, full ranks `[7,8,5,1,6,3,4,2]`.
- **Other pairs:** seeds 42022 and 42023; all six completed without illegal action, combat truncation, guard end; both control/candidate mean placement 7.667, top-four 0/3 and first-place 0/3; paired rank deltas all zero.
- **Reports:** `research/sessions/s-20261102-9a484c57/round-001.md`, `reports/s-20261102-9a484c57/upgrade-paired.json`, `research/knowledge/proposals/s-20261102-9a484c57-001.md`.
- **Recovery:** source and 6 receipts permanently part of repository Git history, plus short-term 30-day Actions backup. No trained checkpoint to recover. No claims about permanent model continuation.
- **Blockers/risks:** competitive gain not demonstrated, sample n=3 per arm, no direct policy-action-disagreement trace. No Arena ranked work.
- **Next hypothesis:** measure counterfactual action disagreements before spending another six full-game samples; only compare candidate strategies that actually diverge from baseline on genuine TavernGym observations.
