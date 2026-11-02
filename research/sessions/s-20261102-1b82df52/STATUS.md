# STATUS — s-20261102-1b82df52

- Round: 001 complete. Hypothesis tested, result **negative / inconclusive**, **not** validated strength improvement.
- Branch: `agent/s-20261102-1b82df52/optimization-001`, created from `main` `6ac59235b8238196a0e6462de77b72413c829372`.
- Code: `0d54a942f57c3d16828b73bf2bbe357db412049c`, safety correction `c9f6d5902a20c0c861b4384ba3015a59af7fdbad`; Action-generated receipts commit `60011dff38c47783eeebcf7c0433f87bc9c9a632`.
- Pull Request: https://github.com/sstxww/reinforcement-learning/pull/17 (draft; **no self-merge**). Check final-head PR CI before integration.
- Actual learning: **512 PPO steps** (256 per variant, seed 71002), real full games: **6**, evaluation seeds: 32001–32003.
- Best verified mean seat-0 placement: **8.00/8** (both models, n=3 each), top-4 rate **0%**; no strength improvement.
- Required own full-game receipt: `experiments/s-20261102-1b82df52/001-32001.json`, placement **8**, decisions **107**, candidate six/eight-seat evidence in `comparison.json`.
- Environment: TavernGym 1.1.0 / source `6d8712c93022ba11`, 4017/447/245 contract.
- Successful run: https://github.com/sstxww/reinforcement-learning/actions/runs/41413617114 ; earlier failed run: https://github.com/sstxww/reinforcement-learning/actions/runs/41412975503 .
- Model storage: GitHub Actions artifact `logscale-s-20261102-1b82df52-41413617114` (artifact ID 13126299055, expires **2027-01-01**); **NOT permanent**.
- Model files after download: `checkpoints/s-20261102-1b82df52/raw.zip` (SHA256 `d8e1453f2a9e888323c82cc59cf4fbafeac6837eb46930b4e096574140c324cb`) and `checkpoints/s-20261102-1b82df52/signed_log1p.zip` (SHA256 `29854cd32e32079dd8a854aabc3a338c97095dabcbb13c701660309ef5fe8267`). Corresponding `.metadata.json` included.
- Restore while artifact exists: `gh run download 41413617114 --repo sstxww/reinforcement-learning --name logscale-s-20261102-1b82df52-41413617114 --dir .`, check SHA256 and engine version, then `MaskablePPO.load(...)`.
- Next: retain safety cap for pilot evaluations; examine forced endings; train far longer and benchmark vs baseline across more seeds; only adopt log encoding if a replicated improvement is shown. Do not write or merge other sessions' work.
