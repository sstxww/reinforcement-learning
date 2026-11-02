# Round 001 · s-20261102-7fd2e223

- Source: main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Work branch: `agent/s-20261102-7fd2e223/optimization-001`
- Hypothesis: a single legal hero-power activation on turns when the V0 baseline would otherwise EndTurn can improve ranking without risking economy/prioritized actions.
- Scope: new isolated policy/evaluator module, independent test and branch-specific workflow. Shared baseline, PPO, common CI and public knowledge index are untouched.
- Simulator contract: upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`, source hash `6d8712c93022ba11`, TavernGym 1.1.0; observe2 4017/447, mask 245.
- Baseline: untouched `BaselinePolicy`, same seeds/seats/opponent bots as candidate.
- Candidate: `IdleHeroPowerPolicy`; respects the exact mask, uses at most one action 4/5 per turn only instead of baseline's EndTurn and never after 60 actions that turn.
- Execution planned on actual GitHub Actions: four independently seeded paired games (73101–73104), 8 full games total, mandatory `Game.is_over()` and receipt validation. A model is not trained: `training_steps=0`, `model_sha256=null`, `checkpoint=null`.
- Evidence paths after a successful actual run: `experiments/s-20261102-7fd2e223/001-<seed>.json`, control `001-control-<seed>.json`, summary `reports/s-20261102-7fd2e223/paired-001.json`.
- Status at code submission: **awaiting actual experiment results**, no winner claim, no fictional match receipt.
- Failure handling: inspect real workflow job log and modify this session's files only; at most two meaningful revisions for one failure signature.
- Scope of interpretation: four paired seeds are an exploratory screen, not proof of generalization or Arena ranking.
