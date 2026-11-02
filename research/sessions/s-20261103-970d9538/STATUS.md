# Status — s-20261103-970d9538 R003

- Session scope: isolated current-main Release→128-step PPO→full-game→durable Release smoke workflow, NOT an algorithm change or Champion promotion.
- Branch: `agent/s-20261103-970d9538/optimization-003`; base main: `e837e7b445cfb74a84fdb871a4bae4ec9e0ce034`.
- Original R001 verified complete baseline seed 96131 receipt [Actions 41507563527](https://github.com/sstxww/reinforcement-learning/actions/runs/41507563527), held on original R001 branch; R001 superseded by main #116.
- R002 code patch superseded by main #125 and #117; do not merge it.
- R003 smoke workflow source authored and triggered, first run 41508812973; corrected test path in own workflow SHA `cfbffc509f4e2fb42a395a137862887d1b0a42d5`.
- Genuine R003 match receipt: **PENDING**. Genuine R003 PPO steps: **PENDING**. Durable R003 Release: **PENDING**. New confirmed strength: **none**. Official Champion: **none**.
- No shared main files modified; no Arena ranked, no user computer or upstream writes.

- [R003 actual Actions 41508855386](https://github.com/sstxww/reinforcement-learning/actions/runs/41508855386) completed **FAILURE at raw model game**, not trainer: original baseline seed 97311 rank7/17turns/57decisions; registered Release SHA verified; real MaskablePPO 128-step continuation to cumulative 1536 succeeded and generated checkpoint SHA `56ac39b408b2579afefdf1b8479c17c5199a44eaeb8e6f02f30d08d67eab2912`.
- Actual raw candidate seed 97312 failed with `RuntimeError: Full-game safety limit exceeded`; no raw model receipt or placement. Publish job skipped; new model retained only as [temporary Artifact 13171229041](https://github.com/sstxww/reinforcement-learning/actions/runs/41508855386/artifacts/13171229041), expires under 30-day retention, not a durable Release. No Champion promotion.
- Authentic original R003 baseline receipt committed at `experiments/s-20261103-970d9538/003-baseline-97311.json`; failure report at `research/sessions/s-20261103-970d9538/failures/003-raw-ppo-safety-limit.md`; compact run data `reports/s-20261103-970d9538/003-128-resume-failure.json`.
- [Own integration Draft PR #167](https://github.com/sstxww/reinforcement-learning/pull/167) created; keep Draft, do not merge without exact-head CI, live main audit and decisive raw-model-game gate.
- Next round should trace authentic failed candidate's action/Buy legal opportunities under same seed without masked fallback; not another identical trainer retry.
