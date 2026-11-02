# Incident 001 — unguarded PPO full-game safety limit

- Session: `s-20261102-e599fa38`; seed **31071**; source commit `0e4724e59ff0916f85fdcf2643cfa38dd22328f5`.
- Genuine Actions log: https://github.com/sstxww/reinforcement-learning/actions/runs/41415158420 (step **Probe unguarded candidate with 300s wall limit**).
- Candidate checkpoint SHA256: `5b66d29acccb4ecefb302f28a86d40aaa981e121fb830bfe1e752923fc602fcb`.
- Engine TavernGym 1.1.0, source hash `6d8712c93022ba11`.

## Reproduction

After fresh 128-step PPO training, invoke:
```bash
python -m tavern_ai.canary --agent-id s-20261102-e599fa38 --seed 31071 --policy model --model checkpoints/s-20261102-e599fa38/model.zip --receipt outputs/raw-31071.json
```
Observed actual exit code **1**. The stack points to `tavern_ai/canary.py:54`:
```text
RuntimeError: Full-game safety limit exceeded
```
The original engine game did **not** reach `Game.is_over()`; no raw receipt is claimed.

## Minimal independent change and verified retest

The opt-in experimental `choose_guarded` validates all model actions against the current 245-element mask and uses legal action **0 (end turn)** only after **32** actions in a turn; otherwise the raw MaskablePPO policy retains control. Invalid actions raise rather than silently falling back.

Full real-engine verification on the **same trained checkpoint/seed**:
- Guarded seed 31071: completed 15-turn game, **141** decisions, **2** guard overrides, placements **[8,6,5,1,2,4,3,7]**, no combat truncation.
- Independent guarded seed 31072: completed 15-turn game, **108** decisions, **0** overrides, placements **[8,2,7,6,4,5,3,1]**.
- Unit suite: **25/25 pass**, including mask safety and budget validation; full Actions run **success**.

## Root-cause boundary and caveat

The evidence confirms a no-progress action-sequence problem in this raw PPO inference path under a 30,000-iteration cap, but does **not** uniquely identify which action sequence or reward mechanism caused it. Budget guard resolves this symptom for seed 31071; it is not a proven universal cure. A guarded outcome must never be reported as a pure PPO outcome. Candidate remains unpromoted.
