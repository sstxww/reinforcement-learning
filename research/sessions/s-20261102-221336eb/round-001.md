# Round 001 — seat-0 decision budget
Session: s-20261102-221336eb
Branch: agent/s-20261102-221336eb/optimization-001
Baseline main SHA: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
Experiment workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41416453477
Executed commit: ef310bfec9e9a7638f0bb0a65b1b08891c6d70b3
Hypothesis: six non-forced seat-0 decisions/turn may reduce compute without rank loss.
Reason: branch-specific bounded policy evaluation avoids concurrent PPO and economy changes.
Learned from: main research/knowledge/INCIDENTS-20261102.md (full-game safety cap);
open reward/upgrade/receipt PRs were not taken as integrated results.
Changes: isolated experiment runner, per-turn wrapper, isolated one-shot Actions workflow, regression tests.
Environment: TavernGym 1.1.0; source 6d8712c93022ba11;
upstream fb61201a557ddd36a411cf44aac51ce4d9b606ce; patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0; observe2 4017/447, masked 245 actions.
Policy SHA256: b6c36fde66042bd15d2af97e1c9fb822c70028c26e02f58aaf06cd56add85db2; no neural model; no checkpoint.
Training steps: 0 (pure strategy ablation). Random seeds: [73101, 73102, 73103, 73104, 73105, 73106].
All 12 games finished Game.is_over; each has 8 placements and real decisions.
Candidate placements: [5, 7, 8, 7, 8, 7]; mean 7; first 0.0; top4 0.0.
Baseline placements: [7, 7, 8, 7, 7, 7]; mean 7.166666666666667; first 0.0; top4 0.0.
Paired delta (lower is better): -0.16666666666666666; differences: [-2, 0, 0, 0, 1, 0].
Total seat-0 decisions: candidate 275, baseline 270;
cap interventions 12.
Illegal actions 0; no combat truncation and no turn-limit endings (validated before save).
Evidence: experiments/s-20261102-221336eb/001-<seed>.json and baseline-<seed>.json;
metrics: research/sessions/s-20261102-221336eb/evaluation.json; run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416453477.
Failure/uncertainty: sample of six pairs, no superiority proven; Candidate rank advantage not established; cap was exercised.
Model status: no candidate weight, Best unchanged; artifact retention 30 days only.
Next hypothesis: test alternative cap after independent sample expansion if interventions are material.
