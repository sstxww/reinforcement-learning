# Versioned candidate checkpoint register (V5 pilot)

`registry.json` indexes **published GitHub Release assets**, not models already independently loaded by this session. SHA256 values come from published release metadata and linked experiment reports; the `pending` verification field must not be marked successful until actual download, hash, load, inference, resume and real-game checks all succeed.

`champion_model_id` is intentionally `null`: current small-sample PPO comparisons do not show reliable strength improvement. Do not treat `latest_published_candidate_id` as a competitive Champion or automatically continue training from it without verification.

Manual verification after setting up the pinned engine and CPU training stack:

```bash
gh release download v2-learning-41413557445 --repo sstxww/reinforcement-learning \
  --pattern model.zip --pattern model.metadata.json --dir checkpoints/source
python -m tavern_ai.checkpoint_integrity checkpoints/source/model.zip --check-engine \
  --expected-sha256 73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a
```

The verifier refuses metadata lacking SHA256 and any mismatch against the current engine fingerprint. Legacy Artifacts without hashed metadata need explicitly audited migration; never silently mark them verified or overwrite the only saved weights.

The branch-owned Action `.github/workflows/experiment-s-20261102-309d57fc.yml` performs a **128-step** bounded resume attempt and live full-game gate. It publishes a separate prerelease only if gates succeed, preserving a proposed candidate without promoting it. Reconcile with existing V1/V2 learning PRs before production integration.
