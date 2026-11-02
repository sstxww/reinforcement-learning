# s-20261102-bedfc382 — STATUS (after verified round 001)

- **Base main SHA:** `6ac59235b8238196a0e6462de77b72413c829372`.
- **Own branch:** `agent/s-20261102-bedfc382/optimization-001`; commits `4e3a015962d5f143e49cbd01fd5061b0665c8c75` (implementation), `0a3671649cfae87f898adf9155aee86efd259d1d` (safe game driver), `a0ae01cfda12d3a148bcda0368abb153f42b7412` (genuine receipts).
- **PR:** https://github.com/sstxww/reinforcement-learning/pull/12 (draft; CI + integrator review required).
- **Actual training:** 512 environment steps (256 control + 256 shaped), 2 terminal rollout episodes per arm.
- **Independent complete games:** 6 (three paired held-out seeds 31011–31013 per arm); all finished; 0 illegal model actions, 0 simulator truncations, 0 turn limit terminations.
- **Our shaped placements:** [8,8,8]; mean 8.00, top4 0%, win 0%; control also [8,8,8]. **No measured increase** under this small budget; no statistically supported conclusion about training at scale.
- **Receipts:** `experiments/s-20261102-bedfc382/001-31011.json`, `001-31012.json`, `001-31013.json`, generated from real Game.is_over() matches by workflow #41413908927.
- **Evidence and exact config:** `research/sessions/s-20261102-bedfc382/metrics-001.json`. Seed 22042, gamma=.99, n_steps=128, train steps 256/arm, alpha control 0/shaped .5. Engine 1.1.0 hash 6d8712c93022ba11, observe2 4017/447, action 245.
- **Training run:** https://github.com/sstxww/reinforcement-learning/actions/runs/41413908927 — success, evidence commit `a0ae01cfda12d3a148bcda0368abb153f42b7412`.
- **Failed first run:** #41413209781; untrained PPO model stalled with original canary 30,000-cycle guard. Fixed via equal 48-actions-per-turn cap for both arms, logged in round-001.
- **Checkpoints:** `outputs/reward/control.zip` SHA256 `c6d2656fd988188f24d69a8bd521dcaeaa1634dadc99671531b63d7273a7236b` and `shaped.zip` SHA256 `2d3d29a47063cb5aad029c0282c90e775a639634f904f19f183e6a415fc40352`.
- **Restore location:** expiring session Artifact at https://github.com/sstxww/reinforcement-learning/actions/runs/41413908927/artifacts/13125934555 (30 days, expires 2026-12-02 UTC). Download and SHA256-verify before use. Not a durable model registry; expired weights are not recoverable from Git.
- **Best result:** no top-four result in 3 own held-out games; score 8.00; insufficient to claim strength.
- **Next:** confirm PR CI; test longer, compute action-type proportions, bootstrap uncertainty on 20+ held-out seeds. Do not change other open Agent PR files or push main.

## Round 002 started
- Isolated new runner: `.github/workflows/experiment-s-20261102-bedfc382-r002.yml` on own branch; actual measurements and receipt pending at creation.
- New planned training: 4096 per arm, 20 held-out paired seeds 32001–32020; artifacts and receipts under `r002` / `002-` prefixes, preserving round 001.
