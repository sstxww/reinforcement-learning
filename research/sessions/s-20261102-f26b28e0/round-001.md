# V5 s-20261102-f26b28e0 R001 — PR integration, independent paired evidence

Base main: `db5e23ae8c218808821327d806b05d2604cfadfb`. Source branch: `agent/s-20261102-f26b28e0/optimization-001`. PR: https://github.com/sstxww/reinforcement-learning/pull/114.

## P0 Integration and concurrency
At initial snapshot there were 75 open PRs (74 Draft, one non-Draft #15 stacked on draft #9). No safe unrestricted merge of those existing PRs. Main passed CI at base. Concurrent agent subsequently merged a canonical paired full-game evidence gate as **PR #140**, commit `0fcd5eede20a7cb038d08fcc0dd6e9426d6cf25d`. Its evaluator `tavern_ai/paired_receipt_gate_v5.py` has seed/seat pairing, fallback diagnostics, per-seed bootstrapped uncertainty and promotion restrictions. To avoid duplicate implementations, this PR removes our initially developed overlapping module, tests and one-off workflow from the final diff. Earlier tested source remains at commit `969a7a3e3559b491ec884ec57050a247b7fe0f5c`; preserving the independent output as concise evidence is the unique integration value.

## P1 Independent genuine run
Own isolated full TavernGym workflow **SUCCESS**: https://github.com/sstxww/reinforcement-learning/actions/runs/41449892693 . Its uploaded artifact #13144187367 was downloaded and verified. Generated honest eight-seat receipt `experiments/s-20261102-f26b28e0/001-65241.json`: seed 65241, seat0 baseline rank **8**, 17 turns, 45 decisions, completed True, engine TavernGym 1.1.0 / source 6d8712c93022ba11; no truncations. This is engineering validation, not model-strength evidence.

The same workflow verified 3 authentic, historical paired full-game model and baseline receipts against canonical model registry. Its actual output is `reports/s-20261102-f26b28e0/001-paired-1408.json`, seeds 99125–99127. Published original 1408-step experimental candidate (SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`): [8,8,8] vs baseline [6,8,8], model-minus-baseline mean rank **+0.667** (worse), top-four 0/3. These are copied from real GitHub Actions generated JSON, not synthetic metrics. Fallback telemetry absent in these receipts: do not assert pure unguarded PPO from this evidence. Neither code nor scores justify Champion promotion.

The original proposed module passed its own regression tests and 3-pair audit in that workflow. Exact-head branch CI for commit `362724d9b141f4cca4de1d540c41c52b5a8f5468` passed https://github.com/sstxww/reinforcement-learning/actions/runs/41450312937 , including session receipt. Removing redundant source and retesting this final evidence-only diff is deliberate.

## P2 Rank-eight root-cause evidence
Canonical report `reports/s-20261102-68099929/003-buy-opportunity.json`: original 1408-step candidate on independent seed 99128, masked-legal BUY on **35 decision states**, 0 BUY selected; baseline chose BUY 14/21 buy-legal decisions. Both ranked eight that seed. This supports a narrow observed BUY omission, not optimal buying decisions or a proven PPO reward/architecture cause. Separate `reports/s-20261102-ba09e2d4/002-action-opportunities.json` shows severe HeroPower/Cancel oscillation over 6000 decisions and failed match; **not** countable as full-game ranked result.

## P1 Remaining high-priority blocker
Shared main `.github/workflows/train.yml` restores only a possibly expiring Actions Artifact and silently retrains from scratch when unavailable. This session intentionally did not modify that integrator-owned file or launch large PPO runs. GitHub Releases contain durable candidates but latest experimental unpromoted checkpoint is not a Champion.

This session: **0 PPO steps, 0 model-controlled games, 1 independent baseline full eight-seat game, 0 Champion promotions, 0 Arena games, 0 new model weights**. Next step: owner-reviewed durable Release-first strict restore, small opportunity-aware diagnostic, then bounded training only after restore and game gates. No direct main pushes or other-agent branch changes.
