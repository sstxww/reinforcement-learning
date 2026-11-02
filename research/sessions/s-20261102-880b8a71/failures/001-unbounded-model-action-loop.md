# Failure 001 — raw PPO model cannot finish genuine eight-seat game

- **Real Actions run**: https://github.com/sstxww/reinforcement-learning/actions/runs/41427593167
- **Job**: 125217859512, terminal `failure`.
- **Source Release**: `v2-learning-41413557445`, successfully downloaded and SHA256 validated `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`; 1,280 cumulative PPO steps.
- **Engine**: TavernGym 1.1.0, `6d8712c93022ba11`, float 4017/card 447/actions 245. Pinned installation and entire Python test suite **58 passed**.
- **Actual continuation**: `python -m tavern_ai.train --steps 128 --seed 42 --resume checkpoints/source/model.zip --out checkpoints/next/model.zip` succeeded; cumulative total **1,408 real PPO steps** (verified), continuation SHA256 `0c871559bde9fabd6700b5d015ab3b4424222d37204e32bfdaba93b028e89e3e`.
- **Raw model game failed** at `python -m tavern_ai.canary --agent-id s-20261102-880b8a71 --policy model --model checkpoints/next/model.zip --seed 23051` with exact `RuntimeError: Full-game safety limit exceeded` in `tavern_ai/canary.py:54`; `Game.is_over()` was false after the hard loop cap. Therefore **no completed raw model game receipt**, no paired eval, no new durable Release, and no Champion promotion.
- **Temporary evidence only**: 30-day Actions Artifact ID `13132134365`, https://github.com/sstxww/reinforcement-learning/actions/runs/41427593167/artifacts/13132134365 includes resumed candidate `model.zip`, schema2 metadata and attestation JSON. Its availability is **not a reliable permanent model archive**.
- **Important separation**: Original source Release is preserved. This 1,408-step candidate was not promoted. Successful weight continuation does not imply a usable policy.
- **Diagnosis**: game stall / non-progress action loop is **confirmed**; exact repeatedly chosen action and legal opportunity distribution remain unmeasured in this run. Related PR #60 shows prior separately trained candidate suffers early END_TURN while another reference executes many repeated actions, but these are not yet v2-specific root causes.
- **Next experiment**: keep the candidate isolated; measure per-turn legal opportunities, raw action trace and state-progress, while separately reporting guarded complete-game behavior as **assisted** and not raw-model strength. Do not bypass gate or expand PPO training budget.
