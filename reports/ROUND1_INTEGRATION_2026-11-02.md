# AutoTavern-AI V1 — Round 1 integration handoff (2026-11-02)

**State:** Evidence gathered, four working branches and Draft PRs exist. Do not merge before each PR's *current head* passes independent CI and workflow conflicts are reviewed. This report records a dated snapshot; GitHub Actions status changes independently.

## Verified real eight-seat games

All listed games ran pinned TavernGym 1.1.0 observe2, source hash `6d8712c93022ba11`, ending without combat truncation or turn-limit termination.

| Agent | PR | Committed complete game | Seed | Seat 0 rank | Controlled decisions | Exact placements |
| --- | --- | --- | ---: | ---: | ---: | --- |
| strategy | [#6](https://github.com/sstxww/reinforcement-learning/pull/6) | `experiments/strategy/seed-11001-9a621f90f601.json` | 11001 | 6 | 52 | 6,3,4,5,7,2,1,8 |
| learning (baseline prerequisite) | [#9](https://github.com/sstxww/reinforcement-learning/pull/9) | `experiments/learning/seed-12001-3df8b8f1aadb.json` | 12001 | 8 | 36 | 8,2,4,5,7,1,6,3 |
| learning (real trained model) | [#9](https://github.com/sstxww/reinforcement-learning/pull/9) | `experiments/learning/v1-model-match.json` | 1302 | 8 | 149 | 8,3,4,6,5,2,1,7 |
| evaluation | [#7](https://github.com/sstxww/reinforcement-learning/pull/7) | `experiments/evaluation/seed-13001-593bf502965e.json` | 13001 | 4 | 51 | 4,1,8,7,2,5,6,3 |
| infrastructure | [#8](https://github.com/sstxww/reinforcement-learning/pull/8) | `experiments/infrastructure/seed-14001-d48c40da599e.json` | 14001 | 7 | 41 | 7,1,6,2,3,8,5,4 |

Game verification from actual GitHub Actions and receipt JSON; initial main smoke game [run 41406564039](https://github.com/sstxww/reinforcement-learning/actions/runs/41406564039) passed 12 tests and a complete eight-seat game.

## Measured experiments

- **Learning:** MaskablePPO actually trained **256 steps** with seed 42; successful [run 41412362662](https://github.com/sstxww/reinforcement-learning/actions/runs/41412362662). Model's independent evaluation seeds 24000–24002: ranks **[8,8,8]**, mean 8.0, top-four 0.0, first-place 0.0. This is engineering evidence only; do not promote Best.
- **Durable candidate:** [GitHub Release v1-learning-9eada5801f99](https://github.com/sstxww/reinforcement-learning/releases/tag/v1-learning-9eada5801f99) contains 17.5MB `model.zip` with SHA256 `dc5195658995358e70c0d565a979b9cf05ccc5e47ae7adaa0a2f078f01cad917`, schema-2 compatibility metadata, and a held-out report. Independent re-download and resume is a separate gate; verify its workflow before claiming it.
- **Previously failed model:** a separate 256-step checkpoint in run 41412048034 failed due to `Full-game safety limit exceeded`. Do not confuse it with the successful release; keep the diagnostic path in `models/registry.json` until triaged.
- **Evaluation's seeded baseline:** seeds 24000–24003: ranks [7,6,8,8], mean 7.25, top-four 0, first-place 0. Comparisons to PPO require paired model/baseline seeds and a larger sample.
- **Strategy paired smoke:** original V0 versus current V1 on seed 1301 yielded ranks 8 vs 8 and both 47 decisions; no verified strategy improvement.

## CI, source, persistence, and cleanup

- Four Draft PRs: #6, #7, #8, #9, **none approved for merge** when this report was prepared.
- Do not mistake the baseline game on one SHA for model evaluation or the final PR head CI. Many Actions were cancelled or failed because concurrent sessions modified the same branches and because workflows redundantly auto-pushed receipts. Review all current heads and remove duplicate triggers only after ownership coordination.
- CI uses real engine bootstrap, environment fingerprint, complete game and receipt checks. Compare current branch SHA against the successful check SHA before promotion.
- Model lifecycle index: `models/registry.json`. Best remains null. The Release is Candidate. Automatic Latest+restore from Release is **not yet validated**; current main train workflow still uses expiring Artifacts.
- Proposed safe cleaner: `scripts/cleanup_temporary.py` (dry-run default, `--apply` only removes regenerable Python caches and never experiments/checkpoints/models); regression test in `tests/test_cleanup_temporary.py`. No mass deletion of valuable history has been performed.
- Only `sstxww/reinforcement-learning` received writes for this effort; upstream simulator remained read-only. No TavernArena ranked games played.

## Next integration steps

1. Check [PR #6](https://github.com/sstxww/reinforcement-learning/pull/6), [#7](https://github.com/sstxww/reinforcement-learning/pull/7), [#8](https://github.com/sstxww/reinforcement-learning/pull/8), [#9](https://github.com/sstxww/reinforcement-learning/pull/9) against the latest heads; refuse merging red/unresolved CI.
2. Validate the independent Release download, model-load, strict compatibility and real 128-step checkpoint continuation. Only after success consider designating a tested Latest candidate.
3. Eliminate redundant Actions push triggers/branch mutation races; retain one genuine receipt per distinct executable candidate/source commit and maintain reproducibility.
4. Use paired fixed seeds and enough games to estimate uncertainty; focus on action loops/economy and masked PPO reward. The only recorded PPO model remains consistently rank 8 on the small evaluation set.
5. After safe PR merges, update README, train workflow and registry on main through the integration flow, ensure main runs a new full game, and validate weekly bounded training plus Release restoration.

## Addendum: actual recovery and V2 data (verified 2026-11-02)

- Actual [Release recovery validation](https://github.com/sstxww/reinforcement-learning/actions/runs/41413508653): original 256-step checkpoint SHA `dc5195658995358e70c0d565a979b9cf05ccc5e47ae7adaa0a2f078f01cad917` was successfully fetched from its durable Release, hash-validated, resumed 128 PPO steps (384 cumulative), and used to complete a full model game (seed 23001, rank 8, 263 controlled actions); all three held-out games seeded 26500–26502 ranked 8. Genuine summaries `reports/learning/release-resume-41413508653.json` and `reports/learning/release-resume-heldout-41413508653.json` were committed to the learning branch. Workflow conclusion was **failure only in a later additional GitHub Release upload step (HTTP 404)**; the resumed 384-step weight is not known to be durably saved. The source 256-step Release is unaffected.
- Actual [V2 incremental PPO run](https://github.com/sstxww/reinforcement-learning/actions/runs/41413557445) completed with **1,024 more steps / 1,280 cumulative** and a durable [Release](https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445), SHA `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. Full game seed 23002 yielded rank 8 (134 decisions). Same four held-out seeds 24000–24003: V1 PPO `[8,8,8,8]`, V2 PPO `[8,8,8,8]`, scripted baseline `[7,6,8,8]`. **No improvement** is supported; Best stays null. V2 is Latest (unpromoted), with independent Release-based restore verification still pending.
- The candidate index has been updated in `models/registry.json` on the Infrastructure PR branch. Main's recovery fallback and latest head CI have not been integrated/verified; do not call main training reliably restartable yet.
