# Round 001 — Mandatory-choice tie-break ablation

- Session: s-20261102-9c463177
- Source main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Branch: agent/s-20261102-9c463177/optimization-001
- Research hypothesis: taking the rightmost among simultaneously legal mandatory-choice actions (30..45) instead of the baseline's leftmost may alter complete-game outcomes.
- Main code change: a **session-only** policy under scripts/choice_tiebreak_s-20261102-9c463177.py. No edits to shared tavern_ai/baseline.py, train.yml, or others' logs.
- Environment contract: TavernGym 1.1.0, source hash 6d8712c93022ba11, 4017 float / 447 cards / 245 legal-masked actions, commit fb61201a557ddd36a411cf44aac51ce4d9b606ce, patch SHA256 1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0.
- Prior evidence: PR #23 (shaping) and PR #22 (factorized encoder) have genuine short training and matches but no verified strength gain; other draft PRs cover card width, reward transforms, upgrade and action loops. All are **unmerged hypotheses** and not this session's results.
- Training: **not applicable**. This is a pure deterministic policy ablation; training steps = 0. No model checkpoints generated.
- Planned independently seeded paired comparison: 39001–39004, two genuine complete eight-player TavernGym games per seed, seat zero candidate vs main baseline; metrics include mean rank, first rate, top-four rate, paired rank differences and number of actual changed decisions.
- Repro command: python scripts/choice_tiebreak_s-20261102-9c463177.py --start-seed 39001 --games 4
- Mandatory session receipt: experiments/s-20261102-9c463177/001-39001.json (exists only if the actual experiment succeeds).
- Actions evidence: https://github.com/sstxww/reinforcement-learning/actions/runs/41415579630 (started, completion to be confirmed).
- Current status: **in progress**. No game results or performance improvement asserted until true engine-backed metrics and receipts are available.
- Failure safety: no fake receipt on error; at most two root-cause changes then record blocker and stop retries.
- Follow-up: compare session metrics and ensure event counts >0 before interpreting placement differences, validate every receipt, inspect PR head CI, and only then propose next hypothesis.
