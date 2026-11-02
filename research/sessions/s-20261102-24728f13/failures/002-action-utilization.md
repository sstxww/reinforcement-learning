# R002 behavioral failure analysis · action utilization

**Type:** competitive/behavioral failure, not runtime/CI exception. No fabricated traceback or claimed code defect.

**Evidence:** own [successful real-engine Actions run 41418438337](https://github.com/sstxww/reinforcement-learning/actions/runs/41418438337), `reports/s-20261102-24728f13/002-action-telemetry.json`, six actual `experiments/s-20261102-24728f13/002-*.json` receipts, all `Game.is_over()`.

**Engine/seed/model provenance:** TavernGym 1.1.0, fingerprint `6d8712c93022ba11`; evaluation seeds 42174–42176; candidate 256-step checkpoint SHA256 `802c65e7da2ba42e26e2f2efb55859b91428f1b792428031947484ce95f42f18`; reference checkpoint SHA256 `8450905bdd1d78e6be68175f9943b16ac840fc9ce2882da4e32791ddb078ad0c`.

**Reproduction:** retrieve the archived genuine output or run `python -m tavern_ai.action_trace_24728f13` after downloading exact R001 model Artifact and installing pinned real TavernGym. Inspect `action_histogram`, `action_categories`, `model_chosen_end_turns` and `guard_forced_ends`. No fake simulator used.

**Observed pathology:**
- Candidate 1e-4: zero buy-slot actions in three complete games, 21 self-selected END_TURN over 36 actions, rank [8,8,8]. No forced safety ends.
- Reference 3e-4: 20 buys but 788 actions in `other_action` raw-ID bucket, 21 guard-forced legal ends, maximum same-action streak 40, rank [8,8,7].
- Both: zero illegal actions, zero combat truncations and no game turn-limit ending.

**Root cause status:** unconfirmed. Does the candidate prefer END_TURN with gold/purchase options available? Are repeated reference actions legal zero-progress operations? This needs a state-change / mask-provenance trace. Current evidence is a descriptive correlation only, not proof of LR causality.

**Attempted fix:** none; deliberate non-mutating diagnostic. Avoid blindly forcing purchases or declaring more actions superior before interpreting action semantics.

**Next independent validation:** trace gold, playable hand / shop affordances and before/after feature hashes for repeated action IDs on new seeds, then propose a single isolated action-selection adjustment. No permission blocker was encountered; no retry required.
