# Round 002 — Paired PPO 16-vs-32 action budgets

- Session: `s-20261102-e599fa38`. Branch: `agent/s-20261102-e599fa38/optimization-002`.
- Initial main: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`. Based on own R001 validated head `9887e95afc579ab47e6ae2b3b5c1d1faf6b3d9f2`.
- Experiment source: `1f8d60ff9e764f94374493c1bb86c61229f5ec35`.
- Actual run: https://github.com/sstxww/reinforcement-learning/actions/runs/41416658875 (**success**); artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41416658875/artifacts/13127314081 (expires **2026-12-02 09:00 UTC**, not permanent).
- Prior evidence: our R001 raw model seed 31071 exceeded 30,000-loop game safety bound. R001 candidate with 32-action legal mask guard finished. Other open PRs #12/#17/#18 used caps 48/45/65 on other experimental models.
- Hypothesis: reducing legal action-0 end-turn cap from 32 to 16 can reduce non-progress inference decisions while retaining complete-game validity. **Not a presumed performance improvement.**

## Implementation / reproducibility

New `tavern_ai/guard_budget_eval.py`, tests `tests/test_guard_budget_eval.py`, and independently triggered bounded workflow `.github/workflows/experiment-s-20261102-e599fa38-r002.yml`. No changes to shared main trainer, canary, baseline or other sessions.

The real pinned TavernGym **1.1.0** engine was installed and verified with source hash `6d8712c93022ba11`, observe2 4017/447/245, upstream commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`. **31 tests passed**. Actual new PPO gradient steps: **0**, as this is an inference policy-budget parameter ablation. Both arms loaded the same own R001 **128-step** MaskablePPO checkpoint, training seed **71879**, SHA-256 `5b66d29acccb4ecefb302f28a86d40aaa981e121fb830bfe1e752923fc602fcb`; GitHub Actions successfully restored that Artifact and verified its hash before any play. It is a temporary checkpoint only.

## Real full eight-seat matches, six held-out paired seeds

| Seed | Rank 16 | Actions 16 | Overrides 16 | Rank 32 | Actions 32 | Overrides 32 |
|---|---:|---:|---:|---:|---:|---:|
| 33001 | 8 | 104 | 6 | 8 | 179 | 3 |
| 33002 | 8 | 118 | 4 | 8 | 147 | 2 |
| 33003 | 8 | 110 | 2 | 8 | 142 | 2 |
| 33004 | 8 | 99 | 1 | 8 | 140 | 2 |
| 33005 | 8 | 107 | 2 | 8 | 139 | 2 |
| 33006 | 8 | 93 | 0 | 8 | 93 | 0 |

All **12/12** actual `Game.is_over()` matches had one guarded PPO seat against 7 official scripted bots, legal masks enforced, zero combat truncations and zero engine turn-limit interventions. Exact original receipts: `experiments/s-20261102-e599fa38/002-33001.json` to `002-33006.json` for cap16; `experiments/s-20261102-e599fa38/controls/002-33001.json` through `002-33006.json` for cap32.

- Mean rank **8.0 vs 8.0**, win **0/6 vs 0/6**, top4 **0/6 vs 0/6**; paired ranks tied in every seed.
- Mean decisions **105.167 cap16** vs **140.0 cap32**; 631 versus 840 total, **24.88% fewer** calls for 16 in this sample.
- Average guard override **2.5 vs 1.8333** per game.
- No observed strength improvement; reduced call counts are **not proven wall-clock speedup**. Both arms remain poor after only 128 earlier training steps, and earlier forced end-turn can sacrifice value on a better model.

Raw machine-readable paired metrics: `reports/s-20261102-e599fa38/round-002.json`. The restoration success does not establish permanent checkpoint storage. Do **not** promote candidate or control as Best. Next research: audit model action/observation repetition, improve semantic progression/reward, evaluate on larger independently seeded paired batches.
