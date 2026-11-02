# Round 001 — Discovery choice position ablation

## Hypothesis and rationale

The main-branch `BaselinePolicy` always picks the **lowest** legal action from band [30,46). A position bias could matter in actual TavernGym games. Isolate the effect of choosing the highest legal option in this band; all other baseline decisions stay unchanged. More importantly, **count the number of real decision states with at least two legal choices**, so zero-exposure trials cannot be mistaken for evidence of equality.

## Provenance

- Session: `s-20261102-d1116e51`
- Base: `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Branch: `agent/s-20261102-d1116e51/optimization-001`
- Initial source commit: `d3c25e60c92cc4d99a0547588e298a279ba23038`
- Authentic engine contract: TavernGym 1.1.0; source fingerprint `6d8712c93022ba11`; pinned upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Observations/actions: observe2 float[4017], cards[447], legal mask[245].
- Historical knowledge consulted: `research/knowledge/INCIDENTS-20261102.md`, `docs/CLOSED_LOOP.md`, open PR #27 zero-refresh-exposure, #28 hold/sell non-gain, #29 upgrade ordering non-gain.
- Avoided overlap with PPO network/reward, sell, refresh, hero power, and upgrading experiments.

## Code changes

- `tavern_ai/discover_choice_experiment.py`: original baseline vs isolated highest-index candidate, real `taverngym.Game`, candidate-controlled game + seeded pairs, explicit legality/engine guards, receipt + exposure metrics.
- `tests/test_discover_choice_experiment.py`: legal-mask prioritization, single-option behavior, fallback equivalence, invalid mask, reporting tests.
- `.github/workflows/experiment-s-20261102-d1116e51.yml`: finite 85-minute isolated runner with authentic engine, unit tests, 7 full eight-seat games and 30-day Artifact fallback, results committed only under this session's namespace.

## Execution plan (not results)

- Real runner: https://github.com/sstxww/reinforcement-learning/actions/runs/41416380388
- Own game seed 49001; heldout matched seeds 49002, 49003, 49004 for each arm.
- Expected workload: one candidate canary plus three baseline and three candidate games.
- PPO steps 0; training config not applicable; no checkpoint, model SHA null.
- Required gate: each receipt has `completed=true` from actual `Game.is_over()`, all eight placements, no simulator truncation or illegal actions.
- Only report rank/first/top-four and paired deltas after successful game execution.
- **At time of initial writing, results were not yet verified.** No competitive improvement is claimed.

## Next hypothesis

If actual 30–45 interventions are rare, instrument the cause, measure opportunities over more independent seeds, and avoid strength claims. If exposed and divergent, assess enough heldout seeds before promoting.
