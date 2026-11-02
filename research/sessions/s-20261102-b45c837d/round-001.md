# s-20261102-b45c837d — V5 round 001: integration and model provenance

- Start main snapshot: 42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c. Main was being modified by independent integrators during this session; verify new HEAD before merging.
- Source instruction: latest Gmail AutoTavern-AI V5 TXT, 953 lines, 27,248 bytes, read fully.
- P0 GitHub inventory: first 68 open PRs, later 65 after other agents merged some. PR #43 (seat-rotation runner) merged at 2ac79f258211356989a6ecbbb4a5614617290bd8; latest main CI pending at that snapshot.
- Candidate PR #25: separate strict receipt validation, six synthetic corruption cases rejected versus legacy 6/6 accepted, three real baseline games, exact-head PR CI #41415480128 succeeded. Not a strategy improvement, merge needs current main CI, isolated ownership and review.
- P1 gap: main train.py supports basic zip/meta and --resume, train.yml restores only 90-day Actions Artifacts, no models/ directory in inspected main. Releases list downloadable-looking model assets but this session did not validate download, hash, actual MaskablePPO load, inference, or optimizer recovery.
- P2 evidence, not this session's own matches: PR #60 reports three rank-8 low-LR PPO games, 0 buys in 36 model decisions and 21 voluntary END_TURN; reference PPO made 20 buys in 875 decisions with forced ends. Causal attribution is unresolved, log legal purchase opportunities and money/board progress before changing rewards.
- This branch contributes checksum-verified model manifests, engine and source provenance checks, hard prohibition of unverified Champion labels and 13 locally passing pytest cases. The unit-test weights are dummy bytes only.
- This session personally trained 0 PPO steps, has no checkpoint and claims no candidate competitive strength. An independent branch workflow is prepared to run a real engine baseline canary; its result must be checked before saying it completed.
- Priority next: verify PR/branch CI, collect authentic receipt, independently audit candidate release recovery, then integrate a single safe train/eval persistence entrypoint. No direct main/upstream/Arena modifications.
