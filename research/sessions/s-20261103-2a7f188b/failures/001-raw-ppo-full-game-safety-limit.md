# F001 — Raw 1408-step PPO did not complete seed 99647

- **Original workflow:** https://github.com/sstxww/reinforcement-learning/actions/runs/41512480342
- **Job:** https://github.com/sstxww/reinforcement-learning/actions/runs/41512480342/job/125507560559
- **Executed source commit:** `f203b1940b5af72d7f86b872af759f0a0005a36a`.
- **Exact model source:** unpromoted V5 1408-step Release `v5-s-20261102-68099929-1408-41428692617`; SHA256 `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`, verified by successful `sha256sum --check` in the original job.
- **Pinned environment:** TavernGym 1.1.0 source hash `6d8712c93022ba11`, observe2 4017 floats, 447 card slots, 245 legal-mask actions.
- **Actual raw command:** `timeout 600s python -m tavern_ai.canary --agent-id s-20261103-2a7f188b --seed 99647 --policy model --model checkpoint/model.zip --receipt outputs/002-99647-model.json`
- **Failure signature:** `RuntimeError: Full-game safety limit exceeded` at `tavern_ai/canary.py:54`. It exited nonzero after reaching the 30000 main-loop iteration bound, not the 600 second wall-time timeout.
- **Observed result:** `raw_game_outcome=failure`, `raw_receipt_exists=false`; no valid eight-seat finished game or placement. Do **not** represent this as rank 8 or promotion evidence. `continue-on-error` was deliberate so negative evidence could be retained; overall workflow success is not candidate-game success.
- **Authentic paired control:** same seed 99647, seat 0, script-baseline against seven built-in bots completed rank 8, 17 turns, 47 decisions, permutation `[8,2,6,4,1,3,5,7]`, no truncations; real original `experiments/s-20261103-2a7f188b/001-99647-baseline.json`, SHA256 `f099672d1dc4a42507936dda82c7109557d2ba8ab1806e6fe10e6d88f8bf97bb`.
- **Original Artifact:** https://github.com/sstxww/reinforcement-learning/actions/runs/41512480342/artifacts/13174760496 (14-day retention), ZIP SHA256 `9e94de38953603d8aa4543906987801494060d16320fef78239abbaf701b5424`; contains the exact baseline receipt and raw-game-status.json. Download rechecked the ZIP and two member SHA256 locally.
- **Cause status:** Exceeding the upper game loop limit is confirmed; a specific choice-loop family is NOT confirmed because this canary did not log raw actions or public before/after states. No new training was attempted. Follow up with bounded same-model, same-seed raw action trace, public-state hashes, legal BUY opportunities, action family, and no-progress count. Keep a failure separate from rankings.
- **Retries:** 1 initial run; no identical rerun and no blind PPO scaling. End of own smoke.
