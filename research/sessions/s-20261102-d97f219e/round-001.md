# s-20261102-d97f219e — Round 001: full-match seeded replay audit

## Hypothesis and rationale
Does TavernGym 1.1.0 replay identical **seat-0 observation, action and legal-mask traces**
when the same seed is executed in a reversed, interleaved sequence of other seeds?
Current seeded evaluation summarizes placement only, which can conceal different
trajectories under the same final rank. This isolated audit exercises the real engine.

## Provenance and overlap
- Pinned main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Branch: `agent/s-20261102-d97f219e/optimization-001`
- Engine required: 1.1.0, source fingerprint `6d8712c93022ba11`,
  observe2 [4017 floats, 447 cards, 245 legal-masked actions].
- Training source: no PPO changes, training steps **0**.
- Other open PRs already cover reward shaping, card embeddings, position and
  purchase-slot heuristics, entropy ablations and checkpoint persistence.
  This branch touches no shared implementations.
- Historical issues: `research/knowledge/INCIDENTS-20261102.md`;
  respect full-game safety limit, no claim from incomplete matches.

## Experimental design
- Genuine eight-seat `taverngym.Game`, unchanged `BaselinePolicy` controls
  seat 0 and official `game.bot_play` controls the seven opponents.
- Seeds: 36011, 36012, 36013; execution order:
  36011, 36012, 36013, 36013, 36012, 36011.
- Hash all consecutive seat-0 `(turn, decision, action, features, cards,
  legal_mask)` values. Compare paired transcript digests, final ranks, game
  duration, decisions, guards and engine identity.
- Each game requires `Game.is_over() == True`; receipt must pass
  `tavern_ai.validate_receipt`.
- Test invocation: `python -m pytest`.
- Real run: `python -m tavern_ai.replay_audit_d97f219e --agent-id s-20261102-d97f219e --seeds 36011 36012 36013 --receipt experiments/s-20261102-d97f219e/001-36011.json --out reports/s-20261102-d97f219e/replay-001.json`.
- No model checkpoint or large rollout expected; compact trajectory hashes only.

## Pending evidence
This file is an experimental protocol, **not** a declaration of completed games.
Populate actual run URL, action counts, ranks, unit tests, determinism result,
CI and PR once the GitHub job completes. If a pair differs, do not declare
deterministic replay. No empirical win-rate improvement is being claimed.
