# Failure 002 — Release creation rejected by GitHub 403 (checkpoint remains temporary)

Source: authentic GitHub Actions custody run [41451915674](https://github.com/sstxww/reinforcement-learning/actions/runs/41451915674), job 125298940226; 2026-11-02T13:23Z.

## Completed positive verification before the failure
- Downloaded training Artifact [13144484155](https://github.com/sstxww/reinforcement-learning/actions/runs/41450695383/artifacts/13144484155) from exact 128-PPO-step continuation run 41450695383.
- SHA256 of real `model.zip` matched **920bfa96370f0a40dcd7cae30e1652f323f27cb7516787e0375a4e8f1b046fc0**. Recovered `model.metadata.json`, 1536 total true timesteps, parent source digest **a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632**. ZIP optimizer component/CRC and TavernGym engine compatibility checks passed.
- Re-deserialized real `MaskablePPO.load` on CPU: `num_timesteps==1536`, action space 245. Validated matching genuine full eight-seat model-only game seed 94433, rank 8, no truncation.
- No competing model, registry, Champion, or historical Release was modified.

## Exact failure
Step `Publish immutable-name research-only checkpoint Release` attempted:
`gh release create v5-s-20261102-aaee3a59-1536-41450695383 ... --prerelease`
with `GH_TOKEN: github.token` and workflow `contents: write`. GitHub rejected API POST:
`HTTP 403: Resource not accessible by integration (https://api.github.com/repos/sstxww/reinforcement-learning/releases)`.
Therefore the workflow conclusion was **failure** and the subsequent published-asset byte-download confirmation step was **skipped**. No durable Release may be claimed.

## Recovery / non-retry gate
Do **not** repeatedly re-run the same release job with the same token permissions. Owner or an authorized integrator must arrange an explicitly permitted Release-writing credential / approved publisher; after permission is resolved, reuse exact existing source Artifact with immutable expected digest and publish `model.zip` plus `model.metadata.json`, then re-download both and verify. The current Artifact has 7-day retention, not permanent custody; no model ZIP was added to Git. If the Artifact expires before proper authorization, mark candidate weights unavailable, **never** fabricate or substitute weights.

Source truth: `models/sessions/s-20261102-aaee3a59/1536-candidate.json` was updated to `durable_release_published_confirmed=false`, `release_attempt_status=failed` and explicit 403 cause. A separate three-paired-game evaluation was queued for descriptive diagnostics, not Champion promotion.
