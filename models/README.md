# Canonical Release-backed model registry and strict archive preflight

The **single source of truth** is the existing **main-integrated** `models/registry.json`,
which currently lists **four** unpromoted durable experimental model Releases.
That registry was incorporated into main by another integrator while this session
was running. This PR **preserves its exact content** and does not fork or replace
its candidate history.

The current `latest` points to 1280-step V2, but `best` and `champion`
remain null. A training count and Release URL are not evidence of strength.

## Two separate levels of integrity checking

- Existing `python -m tavern_ai.registry_integrity`: structural invariants,
  canonical Release identifiers and declared weights hash.
- New `python -m tavern_ai.model_registry`: validates that same manifest,
  with **no second index**.
- Download from the existing actual GitHub Release, then run:

```bash
python -m tavern_ai.model_registry \
  --model-id v2-learning-41413557445 \
  --checkpoint /path/to/model.zip \
  --metadata /path/to/model.metadata.json
```

Preflight verifies the actual checkpoint SHA256 against the existing registry,
schema 1 or 2 metadata, pinned environment, schema-2 catalog/ruleset/source/patch
fingerprints, embedded checksum, ZIP CRC, and presence of policy+optimizer entries.

**Do not call preflight alone a successful model restore.** In a trusted pinned
engine, separately deserialize the model, test legal inference, perform any
independently justified training continuation (including optimizer state),
then real complete eight-seat games with held-out seeds. The accompanying V5
workflow attempts V2 Release download, load/inference and a raw model game,
and must be judged by its actual GitHub Actions outcome.

No Champion is created. Original models and other sessions' data are not changed.
