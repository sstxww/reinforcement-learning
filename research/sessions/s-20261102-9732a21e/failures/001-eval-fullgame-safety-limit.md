# Failure 001 — independent paired evaluation reaches full-game safety limit

**Real run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41427627265 (completed **failure**). Job full log, step “Paired independent heldout”, `tavern_ai.evaluate -> tavern_ai.canary.run`: `RuntimeError: Full-game safety limit exceeded`. Determined before baseline arm of paired evaluation finished; do NOT assign a placement to this failed match, and do NOT invent paired results.

## Successful prerequisites (do not conflate with evaluation pass)

- Original V2 Release `v2-learning-41413557445` downloaded; SHA256 source model `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`, metadata `6f0b433191a8242dcedc627f6be49d1551a82788ce7bfd8e60416ede8146acc0`, exact installed TavernGym engine contract checked.
- Real MaskablePPO continuation: **128 newly executed steps**, source total 1280 -> saved candidate total **1408**, seed 20261102. Training module reported `total_timesteps:1408`.
- Candidate file SHA256: `04799f7e23153dd1728d6e765386ea5f9c17da4075ec7672d17cf4dfb170e185`. Metadata SHA256: `83d4a7d5df6d18b9fcc4816edd14988ab2f4e5768cdd41fa2f670cf2b6df7991`. Model saved in finite-lifetime Actions Artifact [13132927436](https://github.com/sstxww/reinforcement-learning/actions/runs/41427627265/artifacts/13132927436), **not yet a permanent Release**.
- **Genuine pure-candidate complete eight-seat game** seed 83601: rank 8, 15 turns, 117 decisions, placements `[8,4,3,5,2,6,1,7]`, no combat or turn-limit guard. The exact original artifact receipt has been copied unchanged to `experiments/s-20261102-9732a21e/001-83601.json` and verified against its candidate file hash. This is ONE completed match, not proof of improvement.
- Model evaluation on independent seeds 83701–83702 failed while executing a candidate game; **zero successfully completed paired comparisons** are established by this run.
- Action-side root cause is currently **unverified**: the existing simulator safety limit alone does not identify which action loop, available buy, reward, or input feature caused the stall.

## Next evidence-driven repair (at most two)
Change only isolated per-session evaluator to capture action identity, state hashes, legal actions, gold and action budgets at failure; make evaluation report machine-readable failures without claiming that guarded matches are completed. Archive the model as **Rejected / unsafe for Champion** only with immutable SHA and clearly marked failure, and independently verify any Release byte-roundtrip. Do not overwrite Champion/Latest, disable safety limit, or represent a failed game as an eighth-place result. No blind PPO scale-up.

**CI:** the initial PR-head CI #41427848508 ran 78 passed / 1 skipped unit tests, but failed `scripts/check_pr_evidence.py` for missing independent receipt while this remote job was running. The authentic receipt was subsequently recovered from the run Artifact and committed. The PR needs a new exact-head CI before integration.
