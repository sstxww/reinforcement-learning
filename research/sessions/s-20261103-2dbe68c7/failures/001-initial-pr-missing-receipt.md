# Failure 001 — initial PR CI refused missing independent receipt

- **Failure signature:** `Missing independent agent game receipt`.
- **First failed CI:** https://github.com/sstxww/reinforcement-learning/actions/runs/41512858640 on PR #189 head `b8935c78a7042b277a778a26f6445cb84a544c89`; job 125508843044.
- **Verified actual sequence:** `python -m pytest` passed **391 tests, 1 skipped**. The next `python scripts/check_pr_evidence.py` failed because this branch had no committed real original game receipt yet. The CI never reached the pinned-engine/full-game step. This is the correct fail-closed behavior, not an assertion of failed unit tests.
- **Cause:** own independent Actions experiment was still running when the PR CI started. It would be unsafe to make a synthetic or predicted game receipt to silence the gate.
- **Substantive correction #1:** independent real Actions https://github.com/sstxww/reinforcement-learning/actions/runs/41512700446 completed **SUCCESS** in job 125508333948, with pinned TavernGym 1.1.0 engine source hash `6d8712c93022ba11`, complete baseline eight-seat seed 99737, controlled seat 0, 16 turns, 46 decisions, placements `[8,5,3,4,2,6,7,1]` (rank 8), zero truncation, no turn cap. Original immutable runner artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41512700446/artifacts/13175150195 (30-day storage only). **Baseline infrastructure only: zero model/PPO training.**
- Authenticated JSON extracted from original runner log (not synthesized), validated exact game seed/policy/agent/SHA/permutation/guard counters, and committed at `experiments/s-20261103-2dbe68c7/001-99737-baseline.json` in commit `67228123eb70baabf8e8c5fb74ff9bae0cb571da`.
- **Retest:** exact updated-HEAD PR CI must be checked after this commit and documentation updates. Do not treat the original failed run as success or infer model quality.
- **Retries used:** one substantive correction; no repeated identical broken runs. No main merge lock held.
