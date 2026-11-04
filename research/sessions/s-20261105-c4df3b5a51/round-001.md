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
