# Model provenance gate (P1 integration extraction)

This index is **extracted from open draft PR #8** to preserve useful model
provenance without merging its conflicting main training workflow or claiming a
stronger policy. The historical PR reports are evidence for previous runs;
model file bytes were **not downloaded or hash-verified in this integration session**.

Run the offline registry consistency gate:

\`\`\`bash
python -m tavern_ai.registry_integrity
python -m pytest tests/test_registry_integrity.py
\`\`\`

To verify an actual downloaded Release checkpoint, download both \`model.zip\`
and \`model.metadata.json\` from the matching GitHub Release, and use:

\`\`\`bash
python -m tavern_ai.registry_integrity \
  --model-id v2-learning-41413557445 \
  --checkpoint checkpoints/model.zip
\`\`\`

This command checks its bytes against the registry SHA256 and refuses mismatch.
It does **not** verify loading, optimizer restoration, inference, continued
learning or full gameplay; those are separate required gates.

The latest registered **unpromoted** candidate is the V2 1,280-step PPO
checkpoint. Historical held-out seeds 24000–24003 produced ranks 8,8,8,8,
whereas the baseline was 7,6,8,8. No Champion or Best exists.
The reported V1 256-to-384-step recovery on a separate runner was successful,
but a fresh recovery of the latest 1,280-step Release is not established.
Existing main \`.github/workflows/train.yml\` restores from time-limited Actions
Artifacts and may silently restart if they expire; it must not be described as
Release-backed continuous training. Do **not** expand PPO steps until release
restore, action telemetry and paired evaluation gates are implemented.

Source releases:
- https://github.com/sstxww/reinforcement-learning/releases/tag/v1-learning-9eada5801f99
- https://github.com/sstxww/reinforcement-learning/releases/tag/v1-learning-resume-41413508653
- https://github.com/sstxww/reinforcement-learning/releases/tag/v2-learning-41413557445

Related integration blockers:
- PR #8: workflow/main conflict, registry extraction only.
- PR #9: learning code draft; check its final-head CI and schema-2 compatibility.
- PR #15: stacked on #9; cannot merge ahead of dependency.
- PR #25 and #43: main already has matching blobs; avoid duplicate imports.
- PR #60: low-LR PPO action telemetry reports 0 buys and 21 model END_TURN
  selections out of 36 actions on three held-out matches; **not yet proven
  causal**. Compare legal BUY opportunities and state-by-state economics before
  altering rewards, hyperparameters or claiming a fix.

No weights are committed to Git in this extraction.
