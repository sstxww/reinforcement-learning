# s-20261102-880b8a71 — V5 R001 live evidence

- **Current phase:** `partial_ppo_resume_verified__raw_model_game_failed__diagnostic_run_active`.
- Source Release: `v2-learning-41413557445`; independent download/hash pass, SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`.
- **Actual successful PPO continuation:** **1,280 → 1,408 total steps** (exactly +128), `model.zip` SHA256 `0c871559bde9fabd6700b5d015ab3b4424222d37204e32bfdaba93b028e89e3e`. Real independent job: https://github.com/sstxww/reinforcement-learning/actions/runs/41427593167
- **Real full-game gate: FAILED** at seed `23051`, `RuntimeError: Full-game safety limit exceeded` after 30,000 action scheduling cycles. Completed original-model receipts **zero**; do not claim rank.
- **First-run test gate:** 58 passed; engine source fingerprint `6d8712c93022ba11`, observe2 4017/447/245.
- **New persistent checkpoint:** **none**. Training candidate held only as temporary 30-day [Artifact 13132134365](https://github.com/sstxww/reinforcement-learning/actions/runs/41427593167/artifacts/13132134365); source Release still durable.
- **Recovery and diagnostic fix:** separate raw-model action probe, legal mask buy opportunities, public observation hash recurrence, per-turn guard forced ends, and clearly differentiated assisted game receipts.
- **New run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41428666321 — in progress at last observation. Results are not yet known.
- **Promotion:** none, Champion/Best not changed; publication of new Release blocked until pure-model game and independent paired evidence.
- Own branch `agent/s-20261102-880b8a71/optimization-001`, PR https://github.com/sstxww/reinforcement-learning/pull/85 (DRAFT); base main `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`. No main/upstream/Arena changes.
