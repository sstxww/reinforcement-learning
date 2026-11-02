# V5 integration + checkpoint provenance / rank-8 triage (R001)

## Ownership, source, and limits
- Session: `s-20261102-704cec7b`; isolated branch: `agent/s-20261102-704cec7b/optimization-001`.
- Starting main commit: `2ac79f258211356989a6ecbbb4a5614617290bd8` (already includes verified integration PR #43).
- Only repository written: `sstxww/reinforcement-learning`. No upstream changes, ranked Arena, or production Champion promotion.
- Engine contract: TavernGym 1.1.0, `observe2` floats=4017/cards=447/actions=245, source hash `6d8712c93022ba11`.

## P0 actual integration
- Reviewed all 68 open PRs at initial snapshot, identified current-main conflicts, draft dependencies, and failed/negative strategy studies.
- **Merged PR #43** after confirming ready/not-draft, exact head `baee34ae58555dfe7dc57725e958881abfc98f87`, independent full-match CI 41417197476 success, six complete genuine games, no shared strategy edits.
- Squash merge commit `2ac79f258211356989a6ecbbb4a5614617290bd8`; post-merge main Actions run **41426816455 completed success**.
- PR #8: draft and mergeable=false; it contains candidate model registry and known training Release resilience gaps. Not merged wholesale.
- PR #9: draft; full-game and release evidence, but author lists unmet recovery gates. PR #15 targets #9 branch; it must not be merged into main first.
- PR #51 / #60: stacked, draft, report PPO low-ranked pathologies. Preserve their negative evidence; do not promote or merge a policy change blindly.
- Remaining strategy drafts require either CI, independent strength evaluation, compatible dependency resolution, or documentation-only extraction.

## P1 code changes and evidence provenance
- Port the durable Release ledger concept from PR #8 as a small **independent, offline-validated** `models/registry.json`, `tavern_ai/model_registry.py`, and negative integrity tests. The model hashes are experiment-reported until freshly downloaded and matched.
- Champion is **null**; Latest is **the 1280-step experimental model**, not the best-performing model. Never silently assume a published Release ZIP means train resume works.
- Four known durable model records (256, 256, 384, 1280 steps), observed records only; weights are not included in Git.
- Own isolated GH Actions workflow (run 41427360022) exercises registry tests, pinned-engine full-game baseline canary, independent Release SHA/ZIP check, SB3 load and bounded 128-step actual resume smoke. **The outcome must be filled in from the completed workflow, not assumed.**
- main `tavern_ai/train.py` still restores compatible metadata from a specified path; `.github/workflows/train.yml` defaults to a successful **Artifact** rather than a durable **Release**, making automatic continuation after Artifact expiry unproven.

## P2 independent evidence review: the recurring 8th place
- Long-run durable V2 checkpoint: actual 1280 PPO steps (PR #15; Actions 41413557445; Release v2-learning-41413557445). Four independent comparable seeds 24000-24003: V1 [8,8,8,8], V2 [8,8,8,8], script baseline [7,6,8,8]. No measured V1→V2 gain; top4 0/4. Release-based V2 restoration still needs checking.
- **Direct action counts, NOT causal proof:** PR #60's genuine paired six-game action telemetry, seeds 42174-42176 (Actions 41418438337):
  - LR=1e-4 candidate: ranks [8,8,8], 36 actions total, **zero BUY**, 21 policy-chosen END_TURN, zero forced ends.
  - LR=3e-4 reference: ranks [8,8,7], 875 actions total, 20 BUY, 21 forced ends, 40 max equal-action streak, and 788 actions in the 'other' category.
  - Both zero illegal actions and ended Game.is_over=true; no simulator truncation. No strength improvement proved by either arm.
- **Provisional mechanism diagnosis:** candidate may collapse to END_TURN early; reference may loop high-frequency action IDs and need forced ends. The action trace does **not** record per-decision buy-legal opportunities, gold, board/shop value, or before/after observation hashes; therefore neither 'refused affordable BUY' nor 'zero-effect loop' is yet confirmed. LR itself is not a demonstrated causal culprit.
- Non-PPO baseline also frequently places 8th: #43 rotated baseline on seeds 41021/41022 across seats 0/3/6 yielded [8,8,7,7,8,8]. Thus a rank-8 PPO outcome combines possibly weak teacher/opponent gap with model-specific action pathologies.

## Explicit gates and next steps
1. Await exact current-head workflow and PR CI. Preserve own real baseline receipt only if the game completed; baseline evidence **is not model evaluation**.
2. If V2 Release hash/load/128-step resume fails, inspect job logs and fix one root cause before any training expansion. Keep original 1280-step Release untouched.
3. Build a state+legal-mask trace on fresh seeds to distinguish END_TURN despite affordable BUY from legitimate early passes; compare economy and board through time. Avoid blind reward changes or unconditional purchase forcing.
4. Only once restore works and a small behavior fix improves reliable per-decision metrics should paired full games and larger training budgets be considered.
5. No Champion promotion, zero newly claimed improved-rank games, and no Arena MMR assertions.

## Important distinction
This session's fresh training steps and complete-match evidence are **pending workflow verification at document creation**; the cited older runs are other sessions' genuine studies, not falsely attributed to this session.


## Verified execution addendum — source-backed results (2026-11-02)

1. Own V2 Release-recovery run [41427360022](https://github.com/sstxww/reinforcement-learning/actions/runs/41427360022) **SUCCESS**, exact SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, loaded 1280-step MaskablePPO, performed 128 genuine PPO continuation steps to 1408, output probe model saved on runner only and **not preserved as durable weight**. Verified original V2 Release remains durable. Separate baseline game seed 88101: complete, rank 7, 46 decisions / 15 turns, authentic committed receipt.
2. Source-registry conflict resolved by adopting main's richer registry merged via #87, instead of overwriting it. Added fail-closed registry validator and tests; registry now annotates this exact successful V2 Release re-download/resume run. Independent ported-registry run [41428514155](https://github.com/sstxww/reinforcement-learning/actions/runs/41428514155) **SUCCESS**.
3. Own genuine V2 [diagnostic run 41428133644](https://github.com/sstxww/reinforcement-learning/actions/runs/41428133644) **SUCCESS**. Exact released 1280-step PPO model in two full eight-seat games:

   | Seed | PPO rank | Decisions | BUY legal decision-states | Actual buys | Action 1+2 selections | Forced end-turns |
   | --- | ---: | ---: | ---: | ---: | ---: | ---: |
   | 88201 | 8 | 163 | 66 | 0 | 75 | 2 |
   | 88202 | 8 | 143 | 49 | 0 | 132 | 0 |

   Both completed with zero truncated combats and valid placements. Their full per-action public-mask events and full-game receipts are committed in `experiments/s-20261102-704cec7b/002-8820{1,2}.json`. This confirms missed legal-buy opportunities; it **does not** prove every buy would be high value. Public observation hashes changed on raw repeated actions, so do not claim all repeats are no-ops.
4. P3 isolated one-factor candidate: when the raw V2 model proposes action 1 or 2, the public board is empty, and BUY is legal, override to first legal BUY. The intervention is explicitly labeled as an override; model's own raw buying remains distinct. Initial real-game workflow [41428860814](https://github.com/sstxww/reinforcement-learning/actions/runs/41428860814) **FAILED**, after an 88301 reference model full game ranked 8, because the new candidate hit the 40-action soft budget in a mandatory-action state where END_TURN was **illegal**. No completed candidate match or strength claim resulted from that failed run.
5. Repair: `safe_budget_action` now first accepts forced mandatory choice/plays legally instead of inventing END_TURN, preserves explicit guard-vs-model event attribution, and hard-fails at 120 decisions for repeated unresolvable actions. Unit regression tests added. New actual paired workflow has been submitted and **must be independently checked for outcome**. Do not promote on unit tests alone.

P3 result is still conditional until its latest-head workflow proves two matched pairs complete; P4 large-scale training remains blocked without a validated improvement. Champion = null, no scored Arena games, no newly advertised strong PPO model.
