# AutoTavern-AI V1 architecture

Four independent research agents work in separate branches, each providing its own real eight-seat TavernGym match receipt. Every PR passes the CI full-match gate. Human integrator merges reviewed changes into main.

The simulator is downloaded from upstream at an exact commit and patched with the independently SHA256-verified TavernArena observe2 patch. Our repository never modifies upstream. Our policy controls one seat against seven official scripted bots.

- `contract.py`: pinned environment version, source fingerprint and legal action layout
- `baseline.py`: safe deterministic V0 policy
- `env.py`: Gymnasium wrapper using observe2 4017/447 observations
- `model.py`: neural network with card embeddings
- `train.py`: Maskable PPO with checkpoint metadata and resume
- `canary.py`: complete eight-player game with genuine evidence
- `evaluate.py`: fixed-seed held-out evaluation
- `arena_policy.py`: adapter for official client (never auto-enters ranked matchmaking)

V1 does not yet support high-throughput observe2 BatchEnv, eight-learner self-play, GPU training, or indefinite GitHub runners. GitHub Actions performs small bounded CPU steps; checkpoint Artifacts expire and need backups.
