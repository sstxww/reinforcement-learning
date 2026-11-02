# s-20261102-0935f036 R001 — P0 integration and P1 fail-closed champion gate

- Session: `s-20261102-0935f036`; base `main` commit `1afd8297e3c661bee3117ac5301b1ca08d64869b` (snapshot)
- Snapshot: 75 open PRs; 74 Draft; only non-Draft #15 is stacked on still-draft #9 (base `agent/learning/v1`) and reports no V2 performance gain. No merge initiated without safe gating/ownership.
- Main already integrated #90, #106, #79, #108: do not re-import those changes.
- Source Release registry `models/release_inventory_v5.json` has no Champion. Canonical `models/registry.json` has no Best/Champion, latest unpromoted 1,408-step model.
- Engineering issue: supplemental Release inventory validator previously permitted a `review_status=verified` marker ALONE to set Champion, without checking independent gameplay, resume and paired evaluation assertions.
- Change: require explicit positive integrity, continuation, raw-match and paired-evaluation fields plus `safety_fallback_used=false` to make Champion reference structurally valid. This does not attest any real checkpoint.
- Evidence of rank-8 symptom on main: `reports/s-20261102-83d91476/001-buy-opportunity-report.json` observed 0 buys in 74 legal-BUY exposures across 2 authentic games; `reports/s-20261102-ba09e2d4/002-action-opportunities.json` records 2978 Hero Power and 2977 Cancel actions in a bounded, INCOMPLETE raw game. These are observational, not proven causal.
- Training steps in this session: **0**. New model releases: **0**. New Champion: **none**. No large-scale training until evidence/recovery issues close.
- Own real-game gate: branch-isolated GitHub Actions workflow. Receipt pending run; no game or CI success claimed in this initial commit.
- Next: inspect action, preserve actual receipt and exact workflow run; open review PR; do not promote poor PPO.

## Verified own-session CI and match

- [GitHub Actions #41449918161](https://github.com/sstxww/reinforcement-learning/actions/runs/41449918161): **completed / success** for initial commit `9994e83991b27d6082dfb94970734e171b486d07`; synthetic regression tests, pinned engine bootstrap and real eight-seat baseline canary all passed.
- Downloaded [artifact #13144182554](https://github.com/sstxww/reinforcement-learning/actions/runs/41449918161/artifacts/13144182554) and verified the JSON receipt payload; committed `experiments/s-20261102-0935f036/001-831202.json`.
- Real match: seed `831202`, TavernGym `1.1.0` (`6d8712c93022ba11`), baseline (not model), `completed=true`, `turns=15`, `decisions=46`, seat 0 placement **8**, truncated combats 0, turn_limit_end false.
- This is an **engineering baseline game**; not a model-game or PPO improvement.
- Actual own-session PPO training steps: **0**; no candidate checkpoint, no Championship promotion.
- PR CI after adding this receipt remains a separate independent gate (not claimed complete here).
