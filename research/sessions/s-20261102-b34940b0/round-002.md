# Round 002 — separating hero selection from later generic `Choose`

## Hypothesis, context and provenance

- Session `s-20261102-b34940b0`; independent `agent/s-20261102-b34940b0/optimization-002`; base main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- [Draft PR #45](https://github.com/sstxww/reinforcement-learning/pull/45), source commit `a0b692ed302093aadb77a1ad669465b259d02b29`, persisted real evidence commit `f32ce91609518a8d940159b4385236911c1f8c82`.
- Learned from [Round 001](https://github.com/sstxww/reinforcement-learning/pull/32) negative result and from independent unmerged PRs [#34](https://github.com/sstxww/reinforcement-learning/pull/34) and [#38](https://github.com/sstxww/reinforcement-learning/pull/38), which also studied generic choice tie-breaking with mixed/negative preliminary effects. These PRs were not merged or altered.
- Upstream `flow.rs` initializes `Game::new` with `turn: 0` and `Phase::HeroSelect`. Upstream `actions.rs` defines action range **30–45 as generic `Choose`**.
- Single round hypothesis: Round 001 global-last-slot loss is materially driven by changing opening hero selection. Compare `baseline`, `full-last` and `posthero-last` (turn 0 baseline, later turns last) at equal seeds. The third arm does **not** isolate Discover from later targets/trinkets.
- New private files: `tavern_ai/choice_after_hero_s_b34940b0.py`, `tests/test_choice_after_hero_s_b34940b0.py`, and workflow `.github/workflows/choice-after-hero-s-20261102-b34940b0.yml`. No common baseline/model/trainer changes.

## Real execution and reproducibility

- Dedicated [Actions #41416720643](https://github.com/sstxww/reinforcement-learning/actions/runs/41416720643): **success**, 10 unit tests passed; real pinned TavernGym installation and runtime contract validated.
- TavernGym version **1.1.0**, verified source hash `6d8712c93022ba11`, observe2 `4017 float / 447 card / 245 actions`; mask validity checked by the common canary. Seat 0 is controlled by each actual rule-policy arm; seven other seats run real official bots.
- **24/24 full eight-seat games**, all `Game.is_over()`, no illegal action, no truncated combat, no engine turn limit.
- Seeds used: 65201–65204 are development/reused from Round 001; 65301–65304 are **fresh held-out**. Each of 8 seeds played under all three arms.
- PPO steps: **0** (pure deterministic rule-policy ablation). No optimizer, learned model weights, training checkpoint, or model SHA. Version-controlled candidate code SHA256 `066666b27049c092be208df2d4e7a3e56e7f5e4f17e8d05f5bed364fdb86b5a1`.
- True receipts: `experiments/s-20261102-b34940b0/002-<seed>.json` for posthero candidate; `experiments/s-20261102-b34940b0/baseline/002-<seed>.json` and `experiments/s-20261102-b34940b0/full-last/002-<seed>.json` for controls. Compact metrics `research/sessions/s-20261102-b34940b0/metrics-002.json`.

## All eight paired seeds

| Seed | Original baseline | Last in all turns | Last after hero turn |
| --- | ---: | ---: | ---: |
| 65201 (reused) | 4 | 8 | 1 |
| 65202 (reused) | 8 | 8 | 8 |
| 65203 (reused) | 6 | 8 | 8 |
| 65204 (reused) | 5 | 8 | 8 |
| 65301 (fresh) | 8 | 7 | 8 |
| 65302 (fresh) | 6 | 8 | 7 |
| 65303 (fresh) | 8 | 8 | 8 |
| 65304 (fresh) | 8 | 8 | 8 |

Overall mean ranks: baseline **6.625**, global-last **7.875**, posthero-last **7.000** (lower is better). First-place rates: **0/8, 0/8, 1/8**; top4 rates: **1/8, 0/8, 1/8**. Posthero-minus-global paired rank deltas `[-7,0,0,0,+1,-1,0,0]`, average **-0.875**. Baseline-minus-posthero mean **-0.375**, i.e. posthero worse than baseline by 0.375 rank.

**Fresh held-out subset:** means baseline **7.50**, global last **7.75**, posthero last **7.75**; all top4 0/4 and wins 0/4. No held-out improvement from keeping original hero choice. The apparent overall posthero benefit over the global-last arm is driven principally by one reused seed 65201 with first place, and must not be used as promotion evidence.

The first real candidate receipt (seed 65201) records eight-player final ranks `[1,7,5,4,3,6,8,2]`, seat0 rank 1, 52 decisions, 14 turns, `completed=true`, `truncated_combats=0`, `turn_limit_end=false`. The independent fresh candidate seed 65301 finished rank 8 with 53 decisions. The candidate made 39 multi-option generic `Choose` decisions across the eight matches, global-last 67; these are trajectory counts, **not causal effect sizes**.

## Interpretation, failures and next hypothesis

- Engineering gate passed: three real policies, all complete games, independently pinned engine, unmodified common simulation, 10 passing unit tests, compact evidence persisted.
- Research outcome: **no verified performance gain and no clear evidence that hero choice alone explains global last policy weakness**. The hypothesis is unresolved, not a validated upgrade.
- Statistical caveats: n=4 new seeds and n=8 total per arm, highly variable placements; reusable seed 65201 is not held-out evidence. Do not derive confidence of general superiority or Best promotion.
- No runtime failures requiring an engineering fix. Prior R001 generic-choice nomenclature caveat respected.
- Persistent raw policy and metrics are in Git. Dedicated Actions Artifact has 30-day retention and is not permanent checkpoint storage. No cleanup deleted anyone's assets, no ranked Arena games ran, no upstream changes.
- Next independent hypothesis: meaningful `Choose` valuation must use pending-choice kind plus observable candidate strength instead of a fixed positional index. Add instrumentation to detect hero/Discover/target/trinket separately before another strength comparison.
