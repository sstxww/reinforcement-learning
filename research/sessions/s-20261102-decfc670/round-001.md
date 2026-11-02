# Round 001 — Release-first checkpoint audit before further PPO training

Session: s-20261102-decfc670. Work branch: `agent/s-20261102-decfc670/optimization-001`. Starting main: `42f4cf3e5fd6dad68c0779345f9e76f42ca80c9c`.

## P0 integration audit
- Verified that PR #43 (true seat-rotated baseline evaluation) merged as `2ac79f258211356989a6ecbbb4a5614617290bd8`; its head `baee34ae58555dfe7dc57725e958881abfc98f87` passed PR CI #41417197476, with six real baseline games.
- Verified that PR #25 (strict receipt integrity) had completed HEAD `cc3f2c3c07a2644110a0371fcf5acb1a8c6659c1`, CI #41415480128 success and 3 real baseline games; it was merged by another concurrent integrator before this session attempted it.
- PR #15 (V2 PPO checkpoint) depends on V1 PR #9, which remains Draft; do not merge or promote it independently.
- Most research PRs are Draft and many show no advantage, e.g. PPO no-buy telemetry #60, dependent on #51. Avoid blind merges.
- A concurrent integrator was actively advancing `main`, so this session deliberately avoided a conflicting direct merge and chose isolated model-validation infrastructure.

## P1 registry and testable gates
- `tavern_ai/checkpoint_registry.py` checks unique IDs, immutable SHA256, release-location integrity, training step metadata, engine fingerprint, and refuses unverified Champion/latest labels.
- `models/registry.json` inventories published V2 Release `v2-learning-41413557445`, whose GitHub Release API reports model SHA256 `73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a`. Its 1280 steps and poor evaluation are reported by PR #15, not remeasured here.
- No Champion claimed. No long-term resume demonstrated yet. Independent release download, hash check, CPU inference and full baseline game will be run by the branch-specific finite workflow. Until its actual outcome is observed, all remain pending.
- The verifier explicitly distinguishes hash, metadata, CPU load, legal action inference, actual resume, full-game model completion and competitive evaluation.

## P2 evidence informing root-cause experiments
- PR #60 reports a low-LR PPO model with 0 Buy and 21 model-selected End Turn actions in 36 decisions across heldout games (n=3), against a higher-LR reference with 20 buys among 875 actions and 21 forced ends. This is an observational pathology, not proof learning rate caused it. Validate legal-buy opportunities before a behavioral intervention.
- V2 PR #15: four heldout original/new PPO ranks both [8,8,8,8], baseline [7,6,8,8]. No proven rank improvement.
- Next causal probe should log legal Buy opportunities, buy actions, unspent gold, no-progress loops, END_TURN selection and fallback by phase, using the same model and seeds.

## Scope, limits and execution
- PPO training steps this session: 0 so far; no new trained checkpoint. Reusing public Release bytes for verification is not retraining.
- Arena rated games: 0. Upstream writes: 0.
- Own full-game receipt: pending GitHub Actions; do not mark verified before run completes. Planned branch-only receipt: `experiments/s-20261102-decfc670/001-86241.json`.
- No official training, common evaluator, main branch or any other agent's code/files were edited.
- Reproduction: `python -m pytest tests/test_checkpoint_registry_decfc670.py`; `python -m tavern_ai.checkpoint_registry --registry models/registry.json`; with verified release weights: `python -m tavern_ai.checkpoint_registry --model-id v2-learning-41413557445 --model <model.zip> --metadata <model.metadata.json> --cpu-smoke`.
