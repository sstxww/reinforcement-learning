# Round 002 — tighter seat-0 decision budget
Session: s-20261102-221336eb
Branch: agent/s-20261102-221336eb/optimization-002
Baseline main SHA: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
Experiment workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41417053292
Round parent SHA: 9437d569f2097beb383fb116b9998485bb6559bd
Executed commit: 57518ca45244cce7a82b4079743bdce77e7f857b
Hypothesis: three non-forced seat-0 decisions/turn may reduce total decisions despite the unsuccessful six-action pilot.
Reason: branch-specific bounded policy evaluation avoids concurrent PPO and economy changes.
Learned from: main research/knowledge/INCIDENTS-20261102.md (full-game safety cap);
open reward/upgrade/receipt PRs were not taken as integrated results.
Changes: isolated experiment runner, per-turn wrapper, isolated one-shot Actions workflow, regression tests.
Environment: TavernGym 1.1.0; source 6d8712c93022ba11;
upstream fb61201a557ddd36a411cf44aac51ce4d9b606ce; patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0; observe2 4017/447, masked 245 actions.
Policy SHA256: b744d6a7c60f83dec5058af5d0a87ee60becee9cf4da1b02e178a349c4184949; no neural model; no checkpoint.
Training steps: 0 (pure strategy ablation). Random seeds: [73201, 73202, 73203, 73204, 73205, 73206].
All 12 games finished Game.is_over; each has 8 placements and real decisions.
Candidate placements: [8, 8, 8, 8, 8, 8]; mean 8; first 0.0; top4 0.0.
Baseline placements: [8, 8, 6, 5, 7, 6]; mean 6.666666666666667; first 0.0; top4 0.0.
Paired delta (lower is better): 1.3333333333333333; differences: [0, 0, 2, 3, 1, 2].
Total seat-0 decisions: candidate 182, baseline 306;
cap interventions 36.
Illegal actions 0; no combat truncation and no turn-limit endings (validated before save).
Evidence: experiments/s-20261102-221336eb/002-<seed>.json and baseline-002-<seed>.json;
metrics: research/sessions/s-20261102-221336eb/evaluation-002.json; run: https://github.com/sstxww/reinforcement-learning/actions/runs/41417053292.
Failure/uncertainty: cap-3 triggered 36 times and saved 124 decisions (40.5%), but all 6 candidate games ranked last against baseline placements [8,8,6,5,7,6]. Avoid competitive promotion.
Model status: no candidate weight, Best unchanged; artifact retention 30 days only.
Next hypothesis: avoid blunt low decision caps; instrument which actions are sacrificed and test value-aware decisions with independent seeds.
PR (draft, depends on R001 PR #41): https://github.com/sstxww/reinforcement-learning/pull/53
