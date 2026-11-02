# s-20261102-661adf61 STATUS — two bounded rounds completed

- Original main base: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Round 001 branch: `agent/s-20261102-661adf61/optimization-001`; [draft PR #62](https://github.com/sstxww/reinforcement-learning/pull/62), [CI success #41420672288](https://github.com/sstxww/reinforcement-learning/actions/runs/41420672288)
- Current Round 002 branch: `agent/s-20261102-661adf61/optimization-002`, derived only from R001 commit `3f452370f502627ad75c2c83b4da6cfcfbf60da7`
- Round 002 PR: to be opened (dependent on PR #62); no automatic merge
- R001 real training: 80 masked BC updates, 128 weak V0 teacher states, 8 verified complete games; old checkpoint SHA256 `b77aab475a502dacd2c036f4df87cbadd4656299bf5baaa13f16569b04699cd8`
- R002 real training: 80 masked BC updates, 485 official teacher states, 43 new verified complete games (3 training + 40 heldout), **zero PPO timesteps in either round**
- [R002 Actions #41421174913](https://github.com/sstxww/reinforcement-learning/actions/runs/41421174913): success; prior model downloaded and hash checked
- R002 heldout n=10: official bot mean rank 5.10 / top4 40%; V0 and old BC 7.50 / 0%; new BC raw 7.80 / 0%; **REJECT new model promotion**
- New model SHA256 `0e53f1dba1d65e1d8066a5d48f4988c68968b226ba33521eb5666922abcca509`
- New model storage: [run #41421174913](https://github.com/sstxww/reinforcement-learning/actions/runs/41421174913) Artifact #13130016943 `official-bc-s-20261102-661adf61` expires 2026-12-02 09:32:14 UTC; not permanently backed up
- Full compact records: `reports/s-20261102-661adf61/001-masked-bc.json`, `reports/s-20261102-661adf61/002-official-bc.json`; sample standalone receipts `experiments/s-20261102-661adf61/001-*.json` and `002-*.json`
- Important open problem: new BC learned only ~48.4% of held-out official teacher actions and lost 2.7 average rank to the teacher despite larger dataset; next agent should instrument buy-vs-end action choices and stage-level capability
- Recover with version-specific engine, source code at run SHA, and model zip/pt artifacts prior to expiry; no actual Champion, no Arena ranked participation
