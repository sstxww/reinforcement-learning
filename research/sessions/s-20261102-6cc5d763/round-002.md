# Round 002 — pre-purchase capped refresh (experiment pending)

- Session ID: `s-20261102-6cc5d763`; branch `agent/s-20261102-6cc5d763/optimization-002`.
- Explicit main base `315b068bac5ab6d8403c3c9b18f8c101c0cded5d` (read again before R002).
- Hypothesis: when baseline would buy a shop card on turn >=4 while Refresh is legal, one pre-purchase refresh per turn may outperform blind buy-first baseline.
- Learnt from this session's [Round 001 PR #27](https://github.com/sstxww/reinforcement-learning/pull/27): the end-turn/no-buy refresh trigger had **0 activations** in seven real full matches; equal ranks cannot test causal refresh benefit. R001 workflow https://github.com/sstxww/reinforcement-learning/actions/runs/41415018609.
- R002 candidate explicitly tests whether alternative trigger activates, logging `refreshes_chosen` and `refresh_opportunities`; any all-zero cohort fails experiment validity gate.
- Planned 1 mandatory real TavernGym eight-seat game seed 36511, four paired independent holdout seeds 36512–36515 (nine total real games if finished), one agent seat, seven scripted bots.
- TavernGym 1.1.0, source hash `6d8712c93022ba11`, observe2 4017/447/245. Every game must finish with Game.is_over and pass official project receipt validation.
- No PPO gradients, steps=0. No weights or model checkpoint.
- Workflow `.github/workflows/experiment-s-20261102-6cc5d763-002.yml` limited to this branch, 75-minute maximum, separate concurrency group, 30-day evidence Artifact, no push-trigger loop.
- Status at creation: source/tests committed, run and metrics not yet verified.
