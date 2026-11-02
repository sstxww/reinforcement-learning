# s-20261102-d97f219e — Round 001: seeded full-game trajectory reproducibility

## Research hypothesis
The same TavernGym seed and V0 baseline policy should produce identical
seat-0 `(turn, decision_index, action, observe2_features, cards, legal_mask)`
transcripts even when runs are interleaved in reverse seed order.
Final placement equality alone can conceal different action trajectories.

## Historical background and isolation
- Base main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Historical `research/knowledge/INCIDENTS-20261102.md`: full-game loop guard
  and CI/release incidents; do not infer that a loaded model can complete a game.
- Other open PRs already occupy PPO rewards/entropy/embeddings, heuristic
  purchase placement, checkpoint recovery and general evaluation.
- New isolated code `tavern_ai/replay_audit_d97f219e.py`, tests
  `tests/test_replay_audit_d97f219e.py`, and private bounded workflow
  `.github/workflows/replay-audit-d97f219e.yml`.
- No shared `baseline.py`, `canary.py`, `train.yml` or upstream code changed.

## Verified code / environment / run
- Source code commit: `7b2c8e07c8112b919e2526728c12dad36fde5dfb`;
  evidence commit `f1d484ec56a2a6825addde46c28ebadada5d71cb`.
- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415065755,
  conclusion **SUCCESS** (all recorded workflow steps passed).
- PR: https://github.com/sstxww/reinforcement-learning/pull/26
- Python regression tests: **25 passed in 0.12s**.
- Real TavernGym: 1.1.0, source hash `6d8712c93022ba11`,
  pinned upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`,
  verified observe2 patch SHA256
  `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Contract: observe2 float[4017], cards[447], legal-mask[245].
- Command: `python -m tavern_ai.replay_audit_d97f219e --agent-id s-20261102-d97f219e --seeds 36011 36012 36013 --receipt experiments/s-20261102-d97f219e/001-36011.json --out reports/s-20261102-d97f219e/replay-001.json`.
- Six **real full eight-player TavernGym matches**, baseline controls seat 0,
  other seven use `game.bot_play`.
- Seeds executed: 36011, 36012, 36013, 36013, 36012, 36011.
- Every match returned `Game.is_over() == True`; no invalid action,
  combat truncation, or turn-limit end.

## Real game result and independent comparison
- Own receipt: `experiments/s-20261102-d97f219e/001-36011.json` — seed 36011,
  14 turns, **39 controlled decisions**, seat-0 rank **8**,
  placements `[8,3,2,4,5,6,7,1]`, no guards tripped.
- Full report: `reports/s-20261102-d97f219e/replay-001.json`.
- First-pass seed-unique ranks `[8,7,8]`, mean **7.6667**, first 0%,
  top-four 0% (n=3 independent seeds, no strength inference).
- Three same-seed replay pairs all produced identical full decision-trace
  SHA-256 digests:
  - 36011: `24390f75c4181a0a6195d616b7a27346f1fa4f0487b40b84b0a9edb547b6ad8f`
  - 36012: `25d8555986c99a3414df1701ba6a332957d96ae0f8ec9ed2ea0b706772b123c2`
  - 36013: `ad98499e5dc8898af9bd99cefaa543cfe2260d3bd88bef5067d613e62b803dc9`
- Replays reproduce placements `[8,7,8]`; **3/3 identical action
  transcripts** is the engineering outcome.
- Baseline code was not changed; this is not a before/after strength
  improvement. No upgraded Best model. PPO training = **0 steps**.

## Fault handling and storage
- No new failure signature in our verified run; no fix retries needed.
- Session-specific branch isolation and no automatic commit-trigger loop:
  experiment workflow ignores its own evidence-only commits.
- No weights or rollout blobs created. The single valid game receipt, compact
  paired metrics, executable code and research reports are in Git history.
- Uploaded Action Artifact retention 30 days; not a permanent checkpoint.
- PR CI for latest head remains a separate gate; do not merge until it passes.

## Learnings / next hypothesis
Seed-controlled games reproduced full observation/action traces under tested
ordering. This validates a stronger reproducibility check than comparing ranks,
but does not establish universal engine determinism across versions/platforms,
and does not improve the weak V0 competitive performance.

Next independently test whether **two different policies evaluated in reversed
order** preserve each policy's trace and rank for identical seed sets; then
compare policies only after enough held-out seeds and complete-model games.
