# V5 P2 — Evidence-based eighth-place failure diagnosis (2026-11-02)

Session: `s-20261102-902968f5`. **Status: partially supported mechanism, causal diagnosis pending.** This is an engineering interpretation of existing immutable experiment evidence, not a newly executed model match and not a claim about TavernArena rank/MMR. Do not promote a candidate from it.

## 1. Comparable genuine matches (historical, existing branches)

| Experiment | Policy/model | Independent game seeds | Seat-0 placements | Top-4 | Documented caveat |
| --- | --- | --- | --- | --- | --- |
| [PR #15](https://github.com/sstxww/reinforcement-learning/pull/15) | MaskablePPO V1 256-step | 24000–24003 | 8,8,8,8 | 0/4 | genuine engine 1.1.0; no rank gain |
| [PR #15](https://github.com/sstxww/reinforcement-learning/pull/15) | Resumed MaskablePPO V2 1280-step | same four | 8,8,8,8 | 0/4 | +1024 PPO steps did not improve these outcomes |
| [PR #15](https://github.com/sstxww/reinforcement-learning/pull/15) | BaselinePolicy | same four | 7,6,8,8 | 0/4 | mean 7.25; also weak; no high-level competitive reference |
| [PR #60](https://github.com/sstxww/reinforcement-learning/pull/60) | PPO lower LR 1e-4 | 42174–42176 | 8,8,8 | 0/3 | 36 controlled actions, 21 chosen END_TURN, 0 BUY, 0 safety-forced endings |
| [PR #60](https://github.com/sstxww/reinforcement-learning/pull/60) | PPO reference LR 3e-4 | same three | 8,8,7 | 0/3 | 875 actions; 20 BUY, 21 forced END_TURN, longest same-action streak 40 |
| [PR #25](https://github.com/sstxww/reinforcement-learning/pull/25) | BaselinePolicy | 36001–36003 | 8,8,7 | 0/3 | independent receipt integrity experiment, not PPO |

All above are actual completed TavernGym games reported in their owning sessions, not the current session's games. PR #60 fixed the source game engine at TavernGym 1.1.0 / engine hash `6d8712c93022ba11`; engine observation contract is 4017 numeric features, 447 card IDs, 245 masked actions. Results are not equivalent to live Arena MMR.

## 2. Distinguish confirmed symptoms from open causes

**Directly supported by telemetry:**

- One low-LR candidate selected END_TURN 21/36 controlled decisions and selected BUY 0 times in three matches. It finished without guards but always eighth. A loss of useful economy actions is plausible, yet these data do not contain per-decision BUY legal masks, available gold and public shop/board features.
- Another model in the same comparison chose many more actions and bought 20 times, yet required 21 safety-forced legal end turns, with 40 repeated identical actions. More actions are therefore *not* synonymous with better play; the raw `other_action` bucket of 788 needs actual 245-action decoding and observed state-change attribution.
- Paired historical checkpoint comparison in PR #15 found no ranking movement despite 1024 additional PPO steps. Thus further bulk training on the same policy configuration has no demonstrated competitive justification from these seeds.
- The baseline itself is not a strong teacher: main `BaselinePolicy.act` prioritizes first legal mandatory choice, first legal play/magnetize, fixed-turn upgrades and first legal shop purchase, with an 85-action forced-end fallback. Rank-8 baseline matches demonstrate weakness is not exclusively a neural-model defect.

**NOT established / must not state as fact:**

- That BUY was legally affordable when the low-LR candidate chose END_TURN; a zero BUY count alone cannot establish missed opportunities.
- That a specific action class in the 788 `other_action` bucket is a zero-progress loop; repeated IDs require public-state before/after comparison.
- That learning rate itself *caused* collapse: only exploratory seed samples and multiple uncontrolled mechanisms.
- That the 1,280-step release is currently fully restorable from the *release asset bytes* in the main branch; the dedicated V5 128-step continuation must pass live hash/optimizer and model-game gates.
- That rank eight implies one shared bug across PPO and rules baseline.

## 3. Code-level contributing risks to test

1. In `tavern_ai/canary.py`, deterministic model predictions are legally masked but are not intrinsically bounded by useful economic progress; full-game safety limit is a failure outcome, not success. A separate policy-specific guard would change evaluated policy and must be disclosed.
2. In `tavern_ai/train.py`, main's schema-1 recovery path checks `engine` but not a weight checksum or complete optimizer lineage. Main `train.yml` restores last successful temporary Actions artifact, not a durable Release. These are *recovery integrity* problems, not yet proven causes of low rank.
3. In `tavern_ai/model.py`, raw numeric features are clamped to [-500,500] and card embeddings are trained indirectly through sparse PPO signals; embedding semantics/economic priorities are not demonstrated by legal action outputs alone.
4. Baseline buys first legal option rather than maximizing strategic card value, so BC imitation of this baseline might reproduce its weakness. Model vs official TavernGym bot stronger teacher remains experimental.

## 4. Specific next falsifiable test (P2 → P3)

Build a deterministic, **public-observation-only** per-turn model trace with old V2 weight verified by SHA256; for each decision record seed/seat/turn, legal action-family flags (especially BUY 8..15), chosen raw ID/family, public gold/shop/own board-hand features, before/after public-state hash, unused gold at end, forced vs model-selected END_TURN and the streak of identical actions. Use limited authentic 8-seat games across fresh seeds. Construct these counters:

- `end_turn_with_legal_buy` / `end_turn_with_affordable_buy` / `end_turn_without_legal_buy` — do not conflate these.
- `legal_buy_opportunity_count`, `buy_count`, `conditional_buy_rate`.
- `no_state_change_repeated_action_count`, `guard_forced_end_count`, `model_selected_end_count`.
- Per-turn spend vs unused gold, average board size and stage of first sustained inferiority.
- Matched baseline and V2 on held-out seeds with seat rotation and paired rank differences plus uncertainty; model-only results separate from guarded/fallback results.

Only after that diagnosis, test **one** targeted correction in an isolated strategy/training variant (e.g. verified missed affordable buys, not arbitrary forced buys), rerun complete games, and require paired improvement before scaling PPO or modifying a Champion. No Champion currently established. Avoid entering ranked TavernArena.

## 5. Provenance and update gates

- Historical numerical data: [PR #60 exact telemetry](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-24728f13/optimization-002/reports/s-20261102-24728f13/002-action-telemetry.json); [PR #60 failure report](https://github.com/sstxww/reinforcement-learning/blob/agent/s-20261102-24728f13/optimization-002/research/sessions/s-20261102-24728f13/failures/002-action-utilization.md).
- [PR #15 V2 comparable metrics](https://github.com/sstxww/reinforcement-learning/blob/agent/learning/v2/reports/learning/v2-comparison.json).
- Current V5 audited Release lineage and state: `research/sessions/s-20261102-902968f5/STATUS.md`, candidate Release `v2-learning-41413557445`, [PR #84](https://github.com/sstxww/reinforcement-learning/pull/84). The first CI had **92 passed, 1 skipped**, but PR evidence gate lacked this session's genuine game receipt while its separate workflow was still running; this is an incomplete integration gate, not failing unit tests. Do not merge until own live game and latest-head PR CI pass.
