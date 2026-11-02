# s-20261102-73729553 — Round 001, public-observation masked behavior cloning

## Evidence and hypothesis
Base main: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d. Own branch: agent/s-20261102-73729553/optimization-001.
Pinned upstream commit: fb61201a557ddd36a411cf44aac51ce4d9b606ce; patched TavernGym 1.1.0 source: 6d8712c93022ba11; observe2: 4017/447/245.
Previous curated incident: research/knowledge/INCIDENTS-20261102.md (raw PPO model could fail full match). Unmerged PR #60 documented zero buy actions and PR #59 recorded seat sensitivity; neither is a shared confirmed model gain.

Hypothesis: Before scaling PPO, verify a low-capacity policy can imitate basic action *families* from public-only visible states and legality. This is an operational learning probe, not a strength improvement claim.

## Mechanisms verified from source
Pinned upstream crates/taverngym/src/actions.rs partitions 245 actions. Pending choices block other actions; buy legality includes available slots, hand capacity, cast-on-buy and special health payment. Mask is authoritative; gold>=3 alone is not. Pinned crates/taverngym/src/obs.rs publicly encodes own gold, tier, health, buy/refresh/upgrade prices, board and hand counts. No opponent hidden information or RNG is read.

## Implementation and separated metrics
New session-only tavern_ai/bc_probe_73729553.py: 39 own-public/mask/own-action-count features -> 14 action-family logits. Deterministic full-batch masked cross-entropy, 250 updates. The first legal action within predicted family is selected. Teacher is this project's weak BaselinePolicy, not an expert. Train seeds 67010-67012 (3 real full games), unseen teacher test seeds 67020-67021 (2 games), full independent BC canary seed 67029 (1 game), paired rank seeds 67030-67032 (6 games), total planned 12 real complete eight-seat games. Python tests check action partition, masking and observation version. No extra BC end-turn guard. Teacher 85-action protection and only-end-legal occurrences recorded separately.

This experiment does **not** learn card synergy, positioning, or high-level strategy. Training accuracy cannot be called game strength. 0 PPO steps; uses explicit supervision in 250 gradient updates, not PPO.

## Execution status
Await actual GitHub Actions result, metrics, model SHA256, full receipts and CI. Never invent missing results. Runner: .github/workflows/bc-probe-s-20261102-73729553.yml (<=50 minutes, one independent concurrency group, no recurrence loop). True outputs go only to experiments/s-20261102-73729553 and reports/s-20261102-73729553; checkpoint is a small JSON weight matrix with digest, with full regeneration possible from recorded seeds. Expected 30-day artifact is not durable; own branch JSON may be reviewably retained. No claimed Champion; no recommendation to promote pending comparison.

## Next experiment
If imitation works but real rank stays poor, investigate discriminating buy-vs-END using a stronger publicly observable teacher, with immutable held-out game seeds and exact purchase counts. If imitation fails, diagnose label/action masking before any additional PPO.
