# Round 001: discrete action identity guard

**SESSION:** `s-20261105-c4df3b5a51`; **TASK_KEY:** `train/strict-discrete-action-boundary`; **BASE_MAIN:** `c1b828734527bae6141805581693d890cc3bff94`.

## Reproduction and minimal hypothesis

Before the change, `TavernEnv.step` called `action=int(action)`. Python permits `int(3.9)==3`, `int(True)==1` and `int("3")==3`; therefore a legal-mask hit need not prove the policy actually selected a discrete integer action. The narrow hypothesis is that rejecting implicit conversions prevents invalid callers from being misattributed as valid model actions. No causal claim about the historical rank-eight PPO failures is made.

The new pure function accepts both Python and NumPy integer scalar actions and rejects bools, floats, strings, NaNs and arrays. Existing range and legal-mask checks stay in `env.py`. Tests cover the helper and the actual `TavernEnv.step` call boundary with a fake engine; those test inputs are synthetic, **not** TavernGym game evidence.

## Inherited and live context

Main `c1b8287` had green CI #41512315964. Main registry Best/Champion are null, the 1408-step experiment is unpromoted. PRs #225/#125 do not own this path. A separate [Issue #182](https://github.com/sstxww/reinforcement-learning/issues/182) proves CAS task refs do not guarantee single writer merge safety.

## Verification / stopping rules

Run bounded isolated unit tests and an authentic TavernGym 1.1.0 baseline-only eight-seat full game seed 110505, seat 0 against seven engine bots. Only a successful real result stored with unchanged original bytes may enter `experiments/s-20261105-c4df3b5a51/`. A baseline game validates infrastructure, not PPO ability. No new training/Release is implied. Inspect exact-head PR CI after commit, and keep PR unmerged absent a globally enforced integrator and required independent checks.

## Execution ledger (initial)

Helper commit `76667598055a300c2f1b929a0f2782d41bf46e8f`, test commit `0d9a873454a0ec33e34f4f6bef5e2286dffee2f5`, environment fix `4326aa5a92a626903dec021ece9a0cc1948b891f`. Isolated Actions URL, final HEAD and receipt are not yet observed. PPO steps 0; model games 0; baseline game pending; own merges 0; durable checkpoints created 0.

**Next round:** verify genuine game and PR-head tests, then hand off exact commit/run to globally safe integrator. Re-check PR #185, #219, and #223 before any main merge.


## Verified execution (post-run update)

- Actual isolated [Actions #41894584883](https://github.com/sstxww/reinforcement-learning/actions/runs/41894584883) source HEAD `29a4feaecb40553b74005c4efb76d40c14a7a1d4`: job `126800595570` **COMPLETED SUCCESS**. All strict-discrete-action regressions, TavernGym 1.1.0 bootstrap, 4017/447/245 contract, full-game baseline and artifact upload passed.
- Original Artifact [#13355307674](https://github.com/sstxww/reinforcement-learning/actions/runs/41894584883/artifacts/13355307674) ZIP SHA256 `3587846a294cbebf97e33303a00cb3f8bf7bf376ffbebe5568fe5b6876fa9dec`; independently unzipped/CRC checked. Original 519-byte receipt SHA256 `3767e5612b2dab5d40191f5bb842d6b261c31afdea3c639ca27286e7c7f473ed`; committed unchanged to `experiments/s-20261105-c4df3b5a51/001-110505.json`, Git blob `2435f10dd88fe017fc0acd029495636c6ef3bc02` matching original.
- REAL complete **baseline-only** game seed 110505, seat 0 vs seven scripted TavernGym bots: rank 3, placements `[3,1,8,2,7,4,5,6]`, 15 turns, 71 decisions, 0 truncated combats, no turn-limit end. **This is not PPO/raw model performance, not a strength gain**.
- No new PPO steps, checkpoint or Release; official unpromoted 1408-step V5 source remains unchanged, and Best/Champion remain null. No main merge. See `reports/s-20261105-c4df3b5a51/001-verified-baseline-custody.json`.
- Next: open PR, check CI on complete latest PR head (branch baseline workflow is not a substitute), request meaningful review, then hand over to globally exclusive integrator when an actual enforced merge entry exists. Unverified authority remains blocked by issue #182.
