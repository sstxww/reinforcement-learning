# Round 001 — pinned public card/action semantics and a real-game audit

## Hypothesis and boundaries
A source-provenance-aware card index and exact action taxonomy help prevent labels that mistakenly equate all catalog cards with playable cards or text keywords with implemented mechanics. This is a **mechanics/tooling** hypothesis, not a gameplay policy change.

## Environment and reproducibility
- Session `s-20261102-30b45c4d`; original main SHA `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Branch `agent/s-20261102-30b45c4d/optimization-001`; only own uniquely named code/test/workflow/receipt/report/session/proposal paths.
- TavernGym 1.1.0 / pinned upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`.
- Patch SHA-256 from contract: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`; engine source hash `6d8712c93022ba11`; observe2 `4017/447/245`.
- Card file SHA-256 `429305fb9dd53e6c5240bf5219a747602e96d7a0e4bbd19a0d65b8b044ed6168`; client version 36.6.3.253932, server patch 36.6.3.
- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41421933831 (completed success); exact Artifact `13129169561`.
- Commands in workflow: `python -m pytest -q`, `bash scripts/bootstrap_engine.sh`, `python -m tavern_ai.mechanics_audit_s_30b45c4d --source vendor/AutoTavern/crates/taverngym/data/cards.json --seed 83171 --output-dir artifacts/s-20261102-30b45c4d`, `python -m tavern_ai.validate_receipt artifacts/s-20261102-30b45c4d/receipt.json`.
- Unit tests: 33 successful tests in job logs. Training updates/timesteps: **0**; no model checkpoint/model changes.

## Full-game independent receipt — actual result
- Policy: unchanged deterministic V0 BaselinePolicy, not a newly trained network.
- Seed 83171, seat 0 vs seven official scripted bots.
- `Game.is_over()==True`; 18 turns; 60 seat-0 policy actions; 0 illegal actions.
- Placements `[8,2,6,4,3,1,7,5]`; controlled seat = **8**; no truncated combat and no turn-limit end.
- Original receipt `experiments/s-20261102-30b45c4d/001-83171.json`; compact reproducible summary `reports/s-20261102-30b45c4d-001-mechanics-summary.json`.
- **Not a competitive lift:** one baseline game, no candidate policy, no paired seed set. Mean candidate rank and confidence intervals not applicable.

## Observed mechanics diagnostics
- Catalog: 3,983 unique card definitions, observed card vocabulary 3,984 including zero padding; 3,051 entries with no explicit pool membership.
- Explicit pools (not disjoint): minion 245, tier7 12, hero 116, spell 70, trinket 236, timewarp 253.
- Action partition exactly 245 values. This run's action counts: choose 15, play 20, buy 12, upgrade 4, end turn 9; sum 60.
- In reachable public states: 15 pending-choice observations, 0 repeated complete public-observation hashes; these are **sample-dependent observations**, not whole-engine invariants.
- Card text and keyword tags remain `effect_verification=NOT_VERIFIED_BY_TEXT`; no unverified trigger correctness is claimed.
- `CardId(i)` is exported as observe2 `i+1`; zero is padding. Cross-checked against pinned `obs.rs` and Python `N_CARDS=db().len()+1`.

## Scientific status and future experiment
- Mechanism metadata and state/action mapping tested; combat trigger semantics, synergy correctness and model understanding **not** established.
- Next defensible experiment: build targeted tests for public `features[7]` gold, `features[10]` tier and `features[11]` upgrade cost under controlled **real-engine** states; then collect held-out public-state teacher action pairs.
- The card index itself is an expiring 30-day Artifact. Compact summary and original receipt are versioned GitHub files. No training model was generated.
- Must pass PR CI on final head and integrator review before shared knowledge promotion. No upstream/main/other-session writes and no Arena match.
