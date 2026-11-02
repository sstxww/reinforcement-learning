# s-20261102-107cfc34 — Round 001: seated full-game evaluation robustness

## Hypothesis and scope
One-seat-only ranking may conceal seat-conditional outcome variation. Test the **same existing V0 BaselinePolicy** controlling seat 0 versus seat 1 in the genuine eight-player Game, with identical seed values. This is an **evaluation-engineering experiment**, not policy/PPO training and not a competitive upgrade claim.

Started from exact `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`, isolated branch `agent/s-20261102-107cfc34/optimization-001`. Checked 29+ open PRs, no other session-owned files changed. Read AGENTS.md, docs/PROJECT_BACKGROUND.md, ARCHITECTURE.md, SESSION_PROTOCOL.md, CLOSED_LOOP.md, research/knowledge/README.md, INCIDENTS-20261102.md and current Actions. The integrated repository had a four-seed baseline mean rank 7.25, no Best PPO checkpoint established. Separate open PRs explore reward/architecture/hero-power/upgrade/refresh/receipt validation; avoid overlapping them.

## Implementation
- `tavern_ai/seat_balance_107cfc34.py`: no changes to production BaselinePolicy/canary, all eight seats still play real Game; controlled seat receives observe2 bytes, masked legal action, safe per-turn decision budget; all others use official `game.bot_play`; requires `game.is_over()`; records `controlled_seat`, `controlled_placement`, game seed, engine fingerprint, policy SHA256, per-seat decision count and all eight placements.
- `tests/test_seat_balance_107cfc34.py`: rejects incomplete pairs, duplicates, mismatched seat/rank and invalid seat identifiers; tests seat-based mean, top-4, first-place metrics.
- `.github/workflows/experiment-s-20261102-107cfc34.yml`: isolated **push + changed-code paths only** workflow; read-only token, dedicated concurrency, bounded 75-minute job; exact engine bootstrap and fixed 2×2 game grid; validates saved real game receipts; cross-checks seat-0 games against the existing `tavern_ai.canary`; archives only compact results for 30 days; does not auto-commit and has no trigger loop.
- Original run code commit `d9cb67f56ac19b5226b9771553cb5025c9c7b9b5`; follow-up workflow hygiene commit `d34f60744df56d3f111150fd27ab3101031cd95d`.

## Real execution and test gate
**GitHub Actions [run 41416566979](https://github.com/sstxww/reinforcement-learning/actions/runs/41416566979): SUCCESS**; all 23 unit tests passed, actual pinned engine installed; all four independent games ended (`Game.is_over()`), no illegal policy actions, no truncations or turn-limit guards. A fifth canonical seat-0 game with seed 51101 exactly matched probe placement array, decision count, turns and guard values (`CANONICAL_SEAT_0_MATCH=true`).

Environment: TavernGym 1.1.0, source fingerprint `6d8712c93022ba11`, source commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, patched source SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`, observe2 4017 float / 447 card IDs / 245 legal-mask actions. Main trained model not involved: **training steps = 0; policy baseline V0; model SHA/checkpoint = none**. Experimental policy module SHA256 as recorded in receipts: `41fa37e1f0567d2575cbb2320f723f96eca1915c07f7e5b4992e70f178e0f29b`.

| Seed | Controlled seat | Rank | Decisions | Turns | Saved real receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| 51101 | 0 | 8 | 32 | 15 | `experiments/s-20261102-107cfc34/001-51101.json` |
| 51101 | 1 | 7 | 44 | 15 | `experiments/s-20261102-107cfc34/001-51101-seat1.json` |
| 51102 | 0 | 8 | 40 | 14 | `experiments/s-20261102-107cfc34/001-51102.json` |
| 51102 | 1 | 8 | 44 | 18 | `experiments/s-20261102-107cfc34/001-51102-seat1.json` |

Results persisted to `reports/s-20261102-107cfc34/seat-paired.json`: 2 games per seat, mean placement seat0=8, seat1=7.5, paired delta (seat1 minus seat0)=-0.5, both top4=0, both first=0. **Small and confounded** (seat changes hero/opponents), not proof of causal seat bias or competitive improvement; performance `temporarily unproven`. The canonical seat-0 strategy remains unchanged. Four games are engineering acceptance, not statistically sufficient paired strength evaluation.

## Caveats / lessons
- `tavern_ai.validate_receipt` prints `placements[0]` even for a seat-1 receipt; this is *not* the controlled seat's placement. The probe and summary explicitly use `placements[controlled_seat]`; this avoids mistaken evaluation and leaderboard attribution. Do not rewrite shared validator while another PR #25 owns integrity audit.
- Baseline weakness persists; multi-seat testing improves evaluation integrity but does not improve play strength.
- No new failure in this round; prior release 403 and PPO safety-limit issues remain historical/outside this PR. No model is promoted to Best.
- Action artifacts are temporary (30 days). Real receipts and compact metrics are committed here, not a model checkpoint.

## Commands / reproduction
```bash
python -m pip install -e '.[test]'
python -m pytest
bash scripts/bootstrap_engine.sh
python -m tavern_ai.seat_balance_107cfc34 --agent-id s-20261102-107cfc34 --seeds 51101 51102 --seats 0 1 --out-dir experiments/s-20261102-107cfc34 --summary reports/s-20261102-107cfc34/seat-paired.json
```
Run and matching receipts are from the actual GitHub Actions job, not synthetic local simulations.

## Next independent hypothesis
After integration review, test a larger seat-stratified benchmark on **held-out seeds** with a clearly bounded multi-seat budget; do not conclude causal position advantage from n=2. Separate strategy work should focus on fixing the baseline's weak average placements but belongs in another isolated research hypothesis/PR. Current PR target is main; CI to be checked after creation.
