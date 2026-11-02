# Failure 001 — resumed PPO cannot finish real unguarded full match

- Run: https://github.com/sstxww/reinforcement-learning/actions/runs/41427679320 (completed **failure**), real pinned TavernGym 1.1.0.
- Successful prior gates in SAME run: tests, pinned engine build, durable Release asset download, model SHA256 and metadata SHA256 verified, policy loaded, legal inference, optimizer resumed from **1280 to 1408 steps** (128 actual), new model SHA256 `503c527492d3a43ff2be9996c4865d2af8be55a981a5a0308b4dccb316598e8e`.
- Baseline own-session seed 927103 completed with rank 8, 15 turns, 37 decisions: `experiments/s-20261102-902968f5/001-baseline-927103.json`. This is **not** a model success.
- Pure 1408-step resumed PPO at seed 927104 aborted from `tavern_ai/canary.py:54` with `RuntimeError: Full-game safety limit exceeded`; **no completed model receipt** exists. Neither Arena nor simulator truncation was used to hide the failure.
- Model checkpoint is backed up in 30-day [diagnostic Artifact](https://github.com/sstxww/reinforcement-learning/actions/runs/41427679320/artifacts/13132189121); it is **not permanent**, nor Champion.
- Root cause remains unconfirmed until raw model actions, legal BUY opportunities, public state changes and same-action streak are logged. No automatic retry of identical canary seed without code/diagnostic change.
- Diagnostic repair: add a separate *unmodified model policy* trace on the exact failed seed, recovering the exact 1408-step SHA-verified artifact. Report incomplete games as `completed=false`, never forge a match receipt or promote weights. No fallback actions inserted. One bounded replay is a material instrumentation change, not an unmotivated training repeat.
- CI #41427746979 initially failed only because own receipt was not yet available; the subsequent own branch evidence commit has supplied authentic baseline receipt. Check latest-head independent CI.
