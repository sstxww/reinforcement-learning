# AutoTavern-AI · verified recovery and checkpoint custody

## Current truth (2026-11-02, round 1)

- Main is the existing V1 scaffold. The pinned engine was installed by CI run
  [41406564039](https://github.com/sstxww/reinforcement-learning/actions/runs/41406564039):
  TavernGym 1.1.0, \`observe2\` with 4017 floats, 447 card IDs and 245 actions.
- The baseline eight-seat run (seed 1001) completed with placements
  \`[7,3,4,5,1,2,8,6]\`, 16 turns and 46 seat-0 decisions.
- **No Best checkpoint has been independently certified**. Do not interpret a
  first candidate's score or a CI smoke game as an improvement claim.
- Initial \`train.yml\` restores 90-day Actions Artifacts only. **That alone is
  not durable checkpoint custody**. Treat resume as unverified until a
  versioned Release exists, its assets can be downloaded, hashes match and
  an inference/full-game smoke test has passed.
- Active work, source branches, failures and PRs: [Round-1 tracker](../issues/2).
  For a canonical current view use the repository's actual PR / Actions history.

## Protected sources of truth

The Git repository holds scripts, lock/compatibility constants, tests, experiment
receipts and reports. \`models/registry.json\` is a conservative index. Null
\`best\` and \`latest\` mean **not established**, not zero performance.

A candidate Release is tagged \`autotavern-v1-candidate-<run_id>\` and
contains the actual \`model.zip\`, \`model.metadata.json\`, model-controlled
eight-seat receipt, held-out evaluation JSON and a hashed candidate manifest.
Publishing requires all items to agree on the model SHA-256. A Release is
more durable than a temporary Actions Artifact but depends on repository and
release retention; it is not an offsite backup.

## Cloud recovery procedure (not user-local installation)

In GitHub Actions, use Python 3.12, install \`-e '.[train,test]'\`, then
run \`bash scripts/bootstrap_engine.sh\`. The bootstrap script pins
\`fb61201a557ddd36a411cf44aac51ce4d9b606ce\` and validates
the SHA-256 of the observe2 patch. Run \`python -m tavern_ai.contract\`
before touching any checkpoint.

Given a verified candidate Release tag:

\`\`\`bash
gh release download "$TAG" --repo sstxww/reinforcement-learning --dir checkpoints
# Use the model checksum from the associated candidate manifest.
sha256sum checkpoints/model.zip
python -m tavern_ai.train --steps 128 --seed 42 \
  --resume checkpoints/model.zip --out checkpoints/model.zip
python -m tavern_ai.canary --agent-id recovery --seed 22001 \
  --policy model --model checkpoints/model.zip \
  --receipt outputs/recovery-full-match.json
python -m tavern_ai.validate_receipt outputs/recovery-full-match.json
\`\`\`

The metadata and weight archive must be from the **same Release**. Abort on a
hash, catalog, ruleset, patch or source-contract mismatch. Do not restart from
scratch silently when a resume operation was requested.

## Promotion and cleanup rules

\`Latest\` is the verified resume lineage; \`Candidate\` is evaluated but not
promoted; \`Best\` requires independent fixed-seed comparison, multi-game
evidence and reviewer approval. Never mutate the Best release in place.

Do not automatically remove checkpoint files, original rollout datasets,
model provenance or experiment receipts. Run
\`python scripts/cleanup_generated.py\` first to preview only expendable
cache folders. Pass \`--apply\` after results are secured; this command never
deletes \`models/\`, \`checkpoints/\`, \`experiments/\`, \`reports/\`, \`vendor/\`
or \`artifacts/\`.
