# s-20261102-6fc22e71 R001 — V5 P0/P1 integration and raw-vs-guarded evaluation gate

## Scope and provenance

- Agent session: `s-20261102-6fc22e71`; one isolated branch `agent/s-20261102-6fc22e71/optimization-001`.
- GitHub repository: `sstxww/reinforcement-learning` only; upstream simulator read-only; no official Arena.
- Starting main SHA: `db5e23ae8c218808821327d806b05d2604cfadfb`; its full-match main CI run `41432038040` succeeded at inspection.
- Start-time open PR search returned **75 open, 74 Draft, only #15 non-Draft**. This is a snapshot, not an integration lock.
- Main model registry latest registered candidate: `v5-s-20261102-68099929-1408-41428692617` (1,408 PPO cumulative steps, 128 from V2 1,280). GitHub Release `model.zip` digest `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632` as recorded by main. No independent binary download/restore by **this** session. `best = null`, `champion = null`.

## P0: real GitHub review action

Reviewed current main and PR #93 exact head `650f62853a1ffc9a774e295e2959db929c127390`, its recorded successful PR full-match CI `41429285964`, its genuine seed-91031 baseline receipt (rank 8, 14 turns, 51 decisions), and its seven changed files. Wrote concrete integration blocker comment:
https://github.com/sstxww/reinforcement-learning/pull/93#issuecomment-6577790907

The PR's test pins **four** registered models, whereas current main has **five**, and its SHA256 metadata index omits the new V5 1408-step model. Its added branch-only workflow also requests write credentials and pushes from Actions. It requires author/integrator reconciliation and new latest-main CI before merge. **Did not merge #93** or touch its branch.

Other holdbacks:
- #15 depends on still-Draft #9, and small matched V2 comparisons do not show strength gain.
- #103 and #107 are Draft, stacked, and overlap buy-opportunity diagnostics already integrated from other sessions. Preserve their independent evidence; do not double-merge as common instrumentation.
- No PR was merged by **this session**; main retained existing verified integration work.

## P1: additive evaluation integration work (not gameplay improvement)

Added `tavern_ai/paired_evidence_s_6fc22e71.py` and `tests/test_paired_evidence_s_6fc22e71.py`. The tool rejects malformed/incomplete games, invalid eight-seat rank permutations, engine mismatches, duplicate seed-and-seat samples, unpaired comparison seeds/seats and mixed model hashes. It pairs model vs baseline on independent game/seat units (rather than treating actions as independent), reports seed-reproducible bootstrap uncertainty and differentiates **reported guards**, **explicit no-fallback** and **unknown guard reporting**.

The module never loads checkpoints, changes model weights, asserts strength improvement or promotes a Champion. It does not replace the existing main evaluator or model registry; it is an optional conservative evidence check. The `models/release_asset_digests.json` on main already tracks seven Release asset pairs and must remain authoritative. Shared training/evaluation entrypoints are not rewritten in this concurrent session.

First genuine original branch Action [41449960959](https://github.com/sstxww/reinforcement-learning/actions/runs/41449960959) passed its **unit tests**, pinned-engine setup, real complete eight-seat **baseline** game and receipt validation. Actual seed **93461**, controlled seat 0 rank **7**, 13 turns, 35 decisions, placements `[7,4,1,6,5,8,2,3]`, `completed=true`, 0 truncated combats and no turn-limit end. The subsequent git push failed with a real `fetch first` non-fast-forward error because this session committed research notes while that workflow ran. The complete exact receipt was recovered byte-for-byte from archived Artifact [13144825416](https://github.com/sstxww/reinforcement-learning/actions/runs/41449960959/artifacts/13144825416) and committed to `experiments/s-20261102-6fc22e71/001-93461.json` with original source `git_sha=0282bced...`; it was **not fabricated**. To prevent recurrence, workflow changed to a read-only regression and original receipt validation, with `permissions: contents: read`, no repository push and no recurring game. Its next clean run and the exact final-head PR CI must be verified. This is baseline infrastructure evidence only, not PPO strength.

## P2: evidence-based rank-eight diagnosis (no unsupported causality)

- Main's 1,408-step V5 latest experiment records three heldout model placements [8,8,8] vs baseline [6,8,8]. Sample is small and not improved.
- Draft PR #103's six genuine eight-seat games compare three fresh seeds. Its guarded V2 model had **521 legal-BUY decision observations but zero selected buys**, with **12 forced END_TURN**. Action-level decisions are temporally dependent; legal BUY does not necessarily mean strategically optimal BUY.
- Draft stacked PR #107 reports an explicit legal BUY override achieving **46 buys** in three model-assisted games but still ranks [8,8,8], and increased safety-guard reliance. It also observed repeated Play/Cancel cycling. This argues against the unsupported claim that extra buys alone repair placement.

Current best falsifiable next diagnosis is to isolate Play/Cancel choice-state loops, inspect legal choice mask and before/after public-state transitions, and separately report raw PPO vs safety intervention. No gradient training or raw-model games were executed by **this** session, no new checkpoint produced, and no Champion promoted. Do not bulk-train until model restore, raw behavior, and evaluator gates are reliable.

## Recovery and handoff

- Existing durable unpromoted candidate Release: https://github.com/sstxww/reinforcement-learning/releases/tag/v5-s-20261102-68099929-1408-41428692617
- Existing canonical registry: `models/registry.json`, validated structurally on main by `tavern_ai.registry_integrity`; durable Release presence does not prove optimizer resumption from its freshly downloaded bytes.
- New evaluation CLI: `python -m tavern_ai.paired_evidence_s_6fc22e71 --candidate <real-model-receipt.json> --baseline <paired-baseline-receipt.json> --out <report.json>`.
- Source and tests are synthetic input validation only; authentic game evidence must come from the dedicated Action and pass original receipt validation.
- Review current main SHA, any concurrently merged implementation, the exact new PR-head CI, the own genuine match, security of workflow permissions, and any scoring-specific guards before consideration for integration. Do not use official Arena.
