# Status — s-20261102-e4c71b9d

- Latest round: 001 (completed, no observed candidate improvement)
- Base SHA: 6ac59235b8238196a0e6462de77b72413c829372
- Branch: agent/s-20261102-e4c71b9d/optimization-001
- Execution code SHA: 3e222cb4290fe0e1d05d220f1ed5b6bd95f32e68
- Evidence SHA: a5bc1a01e81e7b9555c4bdbecf5abc050adddfd3
- PR: https://github.com/sstxww/reinforcement-learning/pull/18 (draft; requires CI and integrator review)
- GitHub run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413669679 (success)
- Tests: 14 passed
- Actual MaskablePPO training: 128 control + 128 pooled = 256 steps
- Complete real eight-seat matches: 5 (one baseline, two control, two pooled)
- Best verified placement among this session's policies: 8/8;
  model paired mean rank control 8.0 versus pooled 8.0
- Illegal model actions: 0; combat truncations: 0; turn-limit end: false
- A/B report: reports/s-20261102-e4c71b9d/ablation-001.json
- Full receipts: experiments/s-20261102-e4c71b9d/001-32010.json,
  001-32011.json, 001-32012.json; control receipts in reports
- Model artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41413669679/artifacts/13127355102
- Model paths inside artifact: checkpoints/s-20261102-e4c71b9d/control.zip,
  checkpoints/s-20261102-e4c71b9d/pooled.zip
- SHA256 control: 439e3a830978cb0a911e0985109fad2b5619a08e69bcbd436ca2ad83c8314ffa
- SHA256 pooled: 1ab6a4beefe060a38f5152dcdbb0e0473a26be87d058f0a41b571a645282ec2c
- Restore: download artifact (30-day retention), verify SHA256, install
  exact pinned engine and training dependencies, load via MaskablePPO.load.
  Artifact expires 2026-12-02T08:34:39Z; no permanent model store.
- Next: longer-budget controlled training and action-loop controls in an
  isolated experimental module, with >=10 independent held-out seeds.
