# Round 001: Bounded replacement-space experiment

- Session: s-20261102-2d73e890
- Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d
- Branch: agent/s-20261102-2d73e890/optimization-001
- Rule version: pinned TavernGym 1.1.0, source hash 6d8712c93022ba11
- Observation contract: features 4017, cards 447, actions 245
- Action provenance: upstream docs/TAVERNGYM.md at pinned upstream commit fb61201a557ddd36a411cf44aac51ce4d9b606ce
- Model checkpoint: not applicable, fixed rule-policy only
- PPO training steps: 0 (parameter tuning via actual complete games)

## Hypothesis and inheritance

Merged baseline does not voluntarily sell minions (actions 16..22) after a purchase is blocked by limited warband space. Its post-purchase priority always plays hand cards 46..125 and magnetizes 126..195 first. A bounded sale might create space for a better minion; a blind sale might instead destroy a valuable long-term engine. This is a *strategy hypothesis*, not proven game knowledge.

The main knowledge/incident log records PPO full-game nontermination and checkpoint-persistence faults. Many unmerged parallel PRs test BC, Freeze, opening upgrades, hero powers, seat assignment and action tie-breaks. This session isolates sale actions in new files and does not touch those shared modules.

## Code and safety

New tavern_ai/sell_cycle_2d73e890.py: public-observation/legal-mask-only policy with 1/2 sale cap per turn after buying a card that cannot legally play/magnetize, provided no mandatory choice is active. It delegates everything else to original baseline. It counts baseline 85-action forced end separately; this is not learned ability.

New tests/test_sell_cycle_2d73e890.py: action range, mandatory-choice priority, magnetize, budget reset, no premature sale, invalid mask, forced end.

New tavern_ai/sell_cycle_experiment_2d73e890.py: actual eight-seat Game loop using pinned observe2 and real bots; reject incomplete/guarded games.

Training/tuning: complete games for budgets 0/1/2 on seeds 68310-68313; select between 1 and 2 using *training* mean place, with a smaller-budget tie-break.
Independent heldout: 68410-68417, paired baseline=0 vs frozen selected budget (16 complete games). Reporting includes placements, mean ranks, top-four and first rates, action and forced-end counts; short samples cannot establish promotion.

## Repro

python -m pytest tests/test_sell_cycle_2d73e890.py
bash scripts/bootstrap_engine.sh
python -m tavern_ai.contract
python -m tavern_ai.sell_cycle_experiment_2d73e890

Evidence and model status must be updated from actual Actions output, not this proposal. Expected receipt directory: experiments/s-20261102-2d73e890/ and summary at reports/s-20261102-2d73e890/001-summary.json.

## Status

Await actual Actions run, matched candidate receipts, PR CI and numerical evidence. Do not promote or claim game-strength improvement without that evidence.
