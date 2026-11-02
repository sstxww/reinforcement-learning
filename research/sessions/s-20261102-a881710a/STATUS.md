# Status — s-20261102-a881710a

- Round: 001
- Branch: `agent/s-20261102-a881710a/optimization-001`
- Base: `main@315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- State: `engine_probe_verified_pending_pr_ci` until a real Actions run and game receipt are checked.
- Research: engine-native metadata export + action-layout check + public-state probe.
- Training steps: 0.
- Own model checkpoint: none. No policy-strength upgrade asserted.
- CI / engine receipt: own workflow 41421685972 passed; canonical full-game receipt committed; PR CI pending.
- Other branches / main / upstream / ranked Arena: untouched.
- Artifacts (when workflow succeeds): `experiments/s-20261102-a881710a/catalog-full.json`, `catalog-summary.json`, `probe-summary.json`, `001-27862.json`; 30-day Actions retention, *not permanent storage*.
- Recovery: `python -m tavern_ai.mechanics_probe_a881710a --seed 27861 --out experiments/s-20261102-a881710a` after pinned engine bootstrap, followed by the documented canary seed.

## Real verified outcome — own GitHub Actions

- [Engine-backed workflow](https://github.com/sstxww/reinforcement-learning/actions/runs/41421685972) completed success against commit `90344e6a9149c89293194a7dc6417e98240fa203`.
- Tests: isolated 3/3 and full suite 20/20 passed. TavernGym 1.1.0, engine source hash `6d8712c93022ba11`, observations 4017 float/447 card, 245 masked actions.
- Full card catalog: 3,983 native static rows, 66 features each, sha256 `440fcd5f03efdce56efc49699a468f0f7cf5a4bd8f6282e9e3c2a6c8adcab654`. Source-only metadata: **not script effects**.
- Instrumented genuine eight-seat game seed 27861: baseline rank **1**, 54 decisions, 15 turns, completed without combat/turn guard truncation.
- Separate genuine canonical baseline receipt seed 27862: rank **7**, 41 decisions, 15 turns, placements `[7,5,1,6,3,4,2,8]`; real receipt validator passed.
- No new model, no training steps, no competitive-strength gain established; two different seeds are not an A/B comparison. Not a Best-candidate PR.
- Artifact [13130745769](https://github.com/sstxww/reinforcement-learning/actions/runs/41421685972/artifacts/13130745769), 30-day expiry on 2026-12-02; full catalog artifact is not permanently stored.
- Next requirement: final PR CI full-match pass and review; no direct main merge.
