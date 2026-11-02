# 001 — V7 CAS lease did not globally exclude competing merges

**First observed:** 2026-11-02 19:39 UTC. **Signature:** while `coord/autotavern-main-integrate` lease state was `held` for `integrate/pr-164`, another session merged PR #164 and advanced main from `3a745c6f...` to `990acd21...`.

- Acquisition SHA: [23a8e916](https://github.com/sstxww/reinforcement-learning/commit/23a8e916787f88fdfbd2bac17969e8e3f3c1988f).
- Observed conflicting merge: [990acd21](https://github.com/sstxww/reinforcement-learning/commit/990acd21d598a34a554a80c50089a8f1a9423ac4), GitHub PR #164 reports `merged=true`, actual main CI [41511814464](https://github.com/sstxww/reinforcement-learning/actions/runs/41511814464) success.
- Clean release: [d3ea7b4](https://github.com/sstxww/reinforcement-learning/commit/d3ea7b4b5c03829bf8cd6bf579b19911564a53d8) via expected_sha CAS. No forced edits, no lease still held.
- **Confirmed:** successful lease-ref creation does not make unrelated REST merge callers honor it. It prevents another first creation of the same ref, not arbitrary merging.
- **Not confirmed:** branch protection or Merge Queue enforcement; protection GET returned HTTP 403 through this connector and repository rulesets listing was empty. Do not assume absence of protection from 403.
- **Fix hypothesis:** require every merge through an enforced protected single entry with fixed concurrency and current-main + PR exact-head check; otherwise designate one integrator explicitly and block others. A mere unadvertised coordination branch is insufficient. This issue is tracked in [#182](https://github.com/sstxww/reinforcement-learning/issues/182).
- Attempts: one acquisition and one normal CAS release, no retry/force/takeover. No PR merger was attempted after observing the race.
