# Round 001 — source-bound mechanics catalog and real-game legal-action probe

- Session: `s-20261102-a881710a`
- Branch: `agent/s-20261102-a881710a/optimization-001`
- Base main commit: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Origin: AutoTavern `fb61201a557ddd36a411cf44aac51ce4d9b606ce`; observe2 patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`.
- Contract: TavernGym 1.1.0, source hash `6d8712c93022ba11`; 4017 float features / 447 embedding indices / 245 masked actions.
- Hypothesis: We can extract a complete, version-anchored **static** card table, verify action encoding and audit public-observation decision coverage. This makes later mechanism supervision safer without presuming textual effects or hidden information.
- Isolation: new `mechanics_probe_a881710a.py`, dedicated unit tests, one session-only finite Actions workflow, session-owned evidence/report/proposal. No core baseline, PPO, main workflow or others' files modified.
- Difference from concurrent PRs: no imitation policy training, no new strategic policy, no strength claim, no change to shared evaluator.
- Metadata provenance: native `taverngym.card_static`, `card_info`, `layout`, `action_name`; upstream `crates/taverngym-py/src/lib.rs`, `crates/taverngym/src/actions.rs`, `crates/taverngym/src/types.rs`.
- Limits: static `printed_mechanics` are labels, **not proof of trigger semantics**; `static_pool_flags` are not the actual lobby-available card pool. Full card catalog is an expiring Actions artifact, not persisted model knowledge yet.
- Cost guard: one build, unit tests, one instrumented full game (seed 27861), one separately validated full canary baseline match (seed 27862); 55-minute job timeout; no auto-commit, no secret use, no endless run loop.
- Training steps: **0** (mechanism-data foundation, not PPO/BC).
- Match/CI outcome: completed real engine run, no training or strength promotion.
- Quality gates after Actions: verify stdout, artifact/receipt, engine layout, source hash and tests; only then update evidence and open a reviewable PR.
- Next: use verified facts to create held-out rules questions on purchasing/economic choices, and separately test scripted effect triggers with genuine game states.

## Real verified outcome — own GitHub Actions

- [Engine-backed workflow](https://github.com/sstxww/reinforcement-learning/actions/runs/41421685972) completed success against commit `90344e6a9149c89293194a7dc6417e98240fa203`.
- Tests: isolated 3/3 and full suite 20/20 passed. TavernGym 1.1.0, engine source hash `6d8712c93022ba11`, observations 4017 float/447 card, 245 masked actions.
- Full card catalog: 3,983 native static rows, 66 features each, sha256 `440fcd5f03efdce56efc49699a468f0f7cf5a4bd8f6282e9e3c2a6c8adcab654`. Source-only metadata: **not script effects**.
- Instrumented genuine eight-seat game seed 27861: baseline rank **1**, 54 decisions, 15 turns, completed without combat/turn guard truncation.
- Separate genuine canonical baseline receipt seed 27862: rank **7**, 41 decisions, 15 turns, placements `[7,5,1,6,3,4,2,8]`; real receipt validator passed.
- No new model, no training steps, no competitive-strength gain established; two different seeds are not an A/B comparison. Not a Best-candidate PR.
- Artifact [13130745769](https://github.com/sstxww/reinforcement-learning/actions/runs/41421685972/artifacts/13130745769), 30-day expiry on 2026-12-02; full catalog artifact is not permanently stored.
- Next requirement: final PR CI full-match pass and review; no direct main merge.
