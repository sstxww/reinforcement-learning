# V5 restoration failure 001 — erroneous schema-1-only release validator

- Real failing run: https://github.com/sstxww/reinforcement-learning/actions/runs/41427594361
- Job: 125217861889, failing step: Verify exact byte hash, environment, loaded PPO and optimizer.
- Exception: `ValueError: Incompatible checkpoint metadata schema/algorithm`.
- Actual Release metadata extracted from the first failed run's Actions artifact: `schema:2`, `algorithm: MaskablePPO`, `total_timesteps:1280`, plus `compatibility` engine/catalog/ruleset/patch/source fingerprints and `checkpoint_sha256`.
- Verified archive SHA256 from downloaded 17,525,115-byte original V2 zip: `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, identical to both historical PR #15 and embedded digest.
- ZIP includes `policy.pth` and `policy.optimizer.pth`; this presence does not establish optimizer loadability.
- Independent PR #81's cloud job #41427542987 failed at the same schema-1-only check (observed from actual job logs), independently corroborating the root cause.
- Root cause **verified**: newly written auditors assumed schema 1; published checkpoint uses schema 2. Neither attempted MaskablePPO load, PPO continuation or model-controlled full game in the failing runs. No Champion exists.
- Minimal fix attempt 1: allow schema 1 or 2, enforce extra schema-2 SHA and compatibility fields, test valid schema-2 and corruption rejection. Do not bypass hash/optimizer checks.
- Next gate: require new exact branch-head CI, actual CPU model + optimizer load, finite 128-step continuation, complete eight-seat candidate game and independent comparison before declaring recovery. If failure reoccurs, read actual logs before a second meaningful fix.
