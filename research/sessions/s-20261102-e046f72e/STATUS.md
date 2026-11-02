# Session status — s-20261102-e046f72e

- **Branch:** `agent/s-20261102-e046f72e/optimization-001`
- **Base:** `6ac59235b8238196a0e6462de77b72413c829372`
- **Current evidence commit:** `28e83970bdcdc76b2b37b17bbe1ea5deea3515f1`
- **PR:** To be added after creation; base branch `main`.
- **Main research area:** compact neural architecture / masked action stability.
- **Runs:** 41413064111 (failed candidate game), 41413715344
  (failed CLI), **41414170876 (successful)**.
- **Executed training:** 768 total actual fresh PPO environment steps across
  3 attempts. Successfully validated final checkpoint: 128 steps per variant,
  256 steps combined, *not* a 768-step continuously trained model.
- **Strongest verified result:** original rank 8 / compact rank 8 on
  full TavernGym eight-seat seed 26110201. No verified strength increase.
- **Architecture result:** compact 833,014 vs original 1,449,846 policy
  parameters (42.5447% fewer). Speedup provisional, order-biased.
- **Real match evidence:** `experiments/s-20261102-e046f72e/001-26110201.json`
  and `experiments/s-20261102-e046f72e/control-26110201.json`.
- **Metrics:** `research/sessions/s-20261102-e046f72e/training-metrics.json`.
- **Checkpoint Artifact:** https://github.com/sstxww/reinforcement-learning/actions/runs/41414170876/artifacts/13127575014
- **Artifact expires:** 2027-01-01T08:38:46Z; no durable backup,
  so do not claim permanent model persistence.
- **Checkpoint SHA256 (compact):**
  `627c71c1e1dc9007aad4014400ee2414689839c9dbc8151692f2cda8a6934e0b`.
- **Checkpoint SHA256 (original):**
  `d9a777f53f2591441b46e1884d5c8a429881d2221bac523d1162fb7c235e4616`.
- **Restore:** `gh run download 41414170876 --repo sstxww/reinforcement-learning --name compact-s-20261102-e046f72e --dir recovered-s-20261102-e046f72e`;
  verify SHA256, load with `sb3_contrib.MaskablePPO.load`.
- **Outstanding:** PR CI confirmation, warm-up/order confound, multi-seed
  evaluation, zero durable checkpoint store.
- **Next:** randomized AB/BA timing; >=5 training seeds; >=20 independent
  full eight-seat held-out games per candidate before strength claims.
