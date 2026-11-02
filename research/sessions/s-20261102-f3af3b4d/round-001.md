# s-20261102-f3af3b4d / Round 001 — grounded mechanics and card catalog probe

## Hypothesis and ownership

A deployable policy cannot learn rules merely from legal masks and card IDs. First validate the exact pinned TavernGym implementation and produce a reproducible, machine-readable *static* catalog with an independently measured capability checklist. These are prerequisites for later behavior cloning and phase-aware training, not evidence of playing strength.

- Main base: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Branch: `agent/s-20261102-f3af3b4d/optimization-001`.
- Owned paths: `tavern_ai/mechanics_audit_f3af3b4d.py`, `tests/test_mechanics_audit_f3af3b4d.py`, a branch-specific workflow, `experiments/s-20261102-f3af3b4d/`, `research/sessions/s-20261102-f3af3b4d/` and one proposal.
- Upstream commit (read-only): `fb61201a557ddd36a411cf44aac51ce4d9b606ce`.
- Patch SHA256: `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Engine: TavernGym 1.1.0, source hash `6d8712c93022ba11`, observation shape 4017/447, action mask 245.
- Catalog source fingerprint: `c4c42e6ce5060e1b79fbcd5f4edbf6d17495f0f52690072481d690610f7ef6d7`.
- Ruleset ID: `tg36-bc45cfc55a0e5cd6c14c`.

## Verified source facts (not learned-model claims)

- Exact action partitions and mask semantics: upstream `crates/taverngym/src/actions.rs` at the pinned commit.
- Engine card metadata, implementation/scripted flags and card index alignment: upstream `crates/taverngym/src/debug.rs::card_json`, `catalog` and Python `taverngym.catalog_json`, `card_info`.
- Offline controlled state intervention: upstream `Game.debug(set_player)`, `Game.view(0)` (own seat only). The latter is **not** a policy observation, and can contain private data for other seats: this probe never supplies it to the policy.

## Executable falsification plan

1. Install the exact pinned source and checked patch using the existing bootstrap script; fail closed if the binary/source fingerprint differs.
2. Check all 245 runtime action names against the 14 source-defined partitions; check each card's `cid + 1` embedding alignment, uniqueness and engine metadata.
3. On two separately seeded real TavernGym instances, complete eight hero choices, then use *explicitly labelled debug interventions* to test affordability monotonicity, positive-cost mask exclusions, and available legal Freeze/Upgrade/Buy/Refresh/EndTurn transitions.
4. Complete **one genuine eight-seat full match** under the baseline as the required engineering gate; verify the receipt, final placement permutation and lack of truncation.
5. Persist small summary, tagged card metadata database, full-match receipt and a source-grounded limitation statement.

Run entry point: `python -m tavern_ai.mechanics_audit_f3af3b4d --agent-id s-20261102-f3af3b4d --seed 78101 --out-dir experiments/s-20261102-f3af3b4d`.
Unit tests: `python -m pytest tests/test_mechanics_audit_f3af3b4d.py`.
CI/engine results: **not yet verified** at initial commit. Populate only from real workflow outputs, not from planned assertions.

## Reporting and safety constraints

Training steps = **0**. No model checkpoint, strength improvement, high-rank score, hidden-information access or online Arena match is claimed. The generated catalog stores engine-level static flags; those flags do not prove specific battlecry/deathrattle trigger behavior or synergy. Additional card-effect tests must be written before using such labels as verified effects.

The full-match evidence is a single baseline engineering canary, not a statistically powered evaluation. Existing baseline evidence is 4 independent games mean 7.25 (seeds 24000-24003); no claims of a superior model. CI is bounded to one session workflow with finite timeout, and run outputs do not trigger it again.

## Related independent work

PRs #61–#64 perform teacher-cloning pilots; #39 investigates mask recurrence, and #25 validates receipts. This work intentionally avoids shared baseline, PPO trainer, evaluation modules and workflow files owned by those sessions.
