# Session status — s-20261102-d1116e51

- Owner: this independent session only
- Base main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Branch: `agent/s-20261102-d1116e51/optimization-001`
- Hypothesis: change legal 30–45 choice band from lowest-index to highest-index, and measure **actual interventions**.
- Current candidate: `tavern_ai/discover_choice_experiment.py` (isolated strategy, not PPO).
- Proven best: **none promoted**; this session has no model checkpoint.
- Training: **0 PPO steps**, deterministic rule ablation.
- Game workflow: https://github.com/sstxww/reinforcement-learning/actions/runs/41416380388
- Evidence target: `experiments/s-20261102-d1116e51/001-49001.json` and `reports/s-20261102-d1116e51/discover-last-paired.json`
- Status: `completed_for_review`, subject to PR latest-head CI. Seven genuine complete eight-seat games verified, and receipts recovered into this branch from the successful Artifact.
- Model recovery: not applicable; no model trained.
- Follow-up: review full-match completion, decision exposure, paired ranking differences, CI on final PR head.
- Integration: no Best promotion and no merge without verified final-head CI.

## Verified outcome (2026-11-02)

- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416380388; code head d3c25e60c92cc4d99a0547588e298a279ba23038.
- Authentic engine TavernGym 1.1.0, source hash 6d8712c93022ba11.
- Candidate canary seed 49001: Game.is_over true, rank 7, placements [7,5,1,3,2,6,8,4], 14 turns, 56 decisions, 10 policy interventions.
- Three same-seed paired full games (seeds 49002–49004) per arm: baseline ranks [7,7,7], candidate ranks [8,8,8]. Mean 7.0 vs 8.0; first 0/3 and top-four 0/3 in each. Candidate changed a real choice **27 times**. Seven of seven games completed with zero invalid actions/truncations/turn guard.
- Rules-only experiment, PPO steps 0. No new model checkpoint, no Latest/Best promotion.
- JSON: experiments/s-20261102-d1116e51/, reports/s-20261102-d1116e51/discover-last-paired.json.
- Original run concluded failure only at final Git push (branch moved due to our own handoff commits), after tests, real engine, games and artifact upload all passed.
- Original Artifact ID 13128375430, expires 2026-12-02, ZIP SHA256 0f3276f00f68b5609b6305edcb5e6e8eb1dd53176e089b265b75301afe8b478e.
- All eight original Artifact JSON records were retrieved and committed to this branch by GitHub connector. See failures/001-stale-branch-push.md.
- Unique workflow updated to fetch/rebase before evidence push, with one bounded retry. This YAML change was not re-run; evidence recovery itself was confirmed.
- Next: independently verify choice semantics and compare option-value scoring, not indiscriminate last choice. Sample too small to assert a general ranking effect.
