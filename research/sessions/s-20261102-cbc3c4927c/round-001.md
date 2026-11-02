# Round 001 — card encoder bottleneck (preregistered)

- Session: `s-20261102-cbc3c4927c`
- Base: `6ac59235b8238196a0e6462de77b72413c829372`
- Branch: `agent/s-20261102-cbc3c4927c/optimization-001`
- Engine: TavernGym 1.1.0; source hash `6d8712c93022ba11`; 4017 float + 447 card IDs + 245 masked actions.
- Initial hypothesis: replacing 447x8->128 positional card projection with a factorized 447x8->64->128 projection reduces card-tower parameters by >=40%, without breaking finite feature encoding or legal full-match operation.
- Isolation: do not touch existing strategy, evaluation, train, or infrastructure files under PR #6, #7, #8, #9.
- Benchmark: single-thread CPU, batch 16, 8 warm-up/40 timed forward passes; benchmark is not game-strength evidence.
- Training plan: 128 PPO timesteps, seed 22021, hard 1200s process timeout; no checkpoint resume from other sessions.
- Match: separate real full eight-seat model-controlled and baseline-controlled matches on seed 22022; 1000s each, full placements, illegal-action failure, truncation checks.
- Engine fixed upstream: `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Workflow: `.github/workflows/experiment-s-20261102-cbc3c4927c.yml`; pushes receipts only to session branch.
- Status: **PENDING runtime evidence**. No measured training, model quality, or completed match claimed here. Check workflow logs and committed JSONs before merging.
- Reference: main README, AGENTS, PROJECT_BACKGROUND, SESSION_PROTOCOL, knowledge/README, open PRs 6-9; knowledge proposals and session records in main were empty when checked.
- Lessons so far: numerical parameter saving can be verified without making a competitive-strength assertion. A paired seed of one is insufficient to establish an improvement.
- Next experiment: if this run succeeds, repeat 10+ held-out seed pairs with uncertainty intervals and fixed training budgets; compare actual PPO scores for both extractor structures.
