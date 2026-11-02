# Round 001 — Fail closed on assisted PR game receipts

## Inherited ground truth and scope
Complete V7 TXT was read (32,014 original attachment bytes). Live main began at `3a745c6f6a48c65528bcbeb81b8627b8db93f046`, with main CI [41511419671](https://github.com/sstxww/reinforcement-learning/actions/runs/41511419671) ultimately succeeding; later main advanced to `c1b828734527bae6141805581693d890cc3bff94` (not a fixed merge base). Reviewed #179 ready-only stale-base gate and #173/#177 paired guard aliases to avoid double editing their production modules.

## Falsifiable hypothesis and repair
The main PR evidence gate called `validate_integrity` but did **not** examine explicit fallback/guard counters. A structurally complete fixture with `policy=model`, a model SHA, and `fallback_actions=1` would therefore be admitted as independent PR evidence, even though it was assisted. This is distinct from the later paired statistical gate. Implemented `require_unassisted` in `scripts/check_pr_evidence.py`; all six aliases are checked both top-level and in `opportunity_diagnostics.counts`, including malformed count types, and explicit guard flags. Safe zero counters and existing unassisted canary format remain allowed.

Commit chain: [code 3d17b64](https://github.com/sstxww/reinforcement-learning/commit/3d17b6417ce10b88fc30433b0b82ae914cce4a6f), [tests 9f1d777](https://github.com/sstxww/reinforcement-learning/commit/9f1d777003e7c4d03ffee9a6295a66dc5d37b3a1), [one-shot workflow faefde5](https://github.com/sstxww/reinforcement-learning/commit/faefde5854211f18b15ee0275686fbe6243036ef), [original receipt b083037](https://github.com/sstxww/reinforcement-learning/commit/b08303755df6ea7c3ed596da2ee134779fcc93e5).

## Actual bounded cloud work and evidence
Own workflow [#41511972575](https://github.com/sstxww/reinforcement-learning/actions/runs/41511972575) **success**, job `125505822750` shows synthetic regression tests, pinned TavernGym engine and complete original eight-seat game succeeded. Workflow is `contents: read`, 55-minute cap, isolated group and one-shot path trigger, no auto-commit and no shared trainer. No privileged publisher. Original run-generated Artifact `13174045954` downloaded and ZIP extracted; JSON byte SHA256 `ecfa59cbfc800689d148c58ccd18e2979d0f64ebf0851dbebc65f34d1596b6d4`. Original JSON in `experiments/s-20261103-296565b1/001-94773.json`.

Game: seed 94773, seat 0 versus seven scripted bots, **baseline** rank **8**, placements `[8,5,1,3,7,2,6,4]`, 14 turns and 48 actual policy decisions, `completed=true`, `truncated_combats=0`, `turn_limit_end=false`, pinned 1.1.0 source `6d8712c93022ba11`, `observe2` layout 4017/447/245. Guard/fallback interventions not present in canary receipt. **This is infrastructure evidence only.** Not a PPO model test and not a strength claim.

## Honest limits, learning, next
PPO steps added **0**; source reference V5 1408-step Release not reloaded/trained; no new optimizer, weights, Release, model promotion or paired held-out evaluation. The raw PPO eighth-place cause is still an open algorithmic problem, with other active PRs. This session edited only its own branch and reviewed #179 through an issue comment; acquired no exclusive integrator lock. A PR-level CI job on this final documentation head and integration-owner review are still required. Model promotion and main verification remain **not done**, not passed.

Next action: inspect PR created from this branch, rerun/check latest-head CI, verify receipt digest, and serialize integration against the then-current main under V7 lock. Consider separately curating this PR's proof-only workflow after merge to avoid dormant experiments; do not delete the only authentic receipt.
