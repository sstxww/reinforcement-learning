# s-20261102-717d0e50 — Round 002 (new independently based branch)

Hypothesis: adding a public-shop tier/stat heuristic and an already-frozen guard to the round-001 Freeze timing policy may avoid blindly preserving weak shop cards and avoid accidentally unfreezing next turn.

Sources: round-001 experiment and https://github.com/sstxww/reinforcement-learning/pull/40. Round-001 ten-seed candidate mean rank 7.7 vs baseline 6.9 (no proven benefit).

Base main SHA: 315b068bac5ab6d8403c3c9b18f8c101c0cded5d.
Branch: agent/s-20261102-717d0e50/optimization-002. Independent of the round-001 branch; it does not cherry-pick another agent's changes.
Method: compare baseline, blind Freeze copied as a self-contained independent control, and quality-aware Freeze on ten new seeds 29201..29210, thirty genuine full eight-player matches. Threshold: shop minion tier >= max(2, tavern tier - 1), attack+health >=5, never toggle already-frozen shop. Features are public observe2 only. Official engine version/fingerprint, 4017/447/245 and runtime layout are checked.
Actual PPO training steps: 0 (strategy experiment). No checkpoint. Engine results and conclusion are pending an actual workflow execution; never infer completion from YAML alone.

Receipt namespace: experiments/s-20261102-717d0e50/002-<seed>.json; also blind2/control2 for matched controls. Metrics: research/sessions/s-20261102-717d0e50/metrics-002.json.
