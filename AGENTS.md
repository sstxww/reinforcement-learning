# Agent Operating Rules — AutoTavern-AI V1

Read `docs/PROJECT_BACKGROUND.md`, `docs/SESSION_PROTOCOL.md`, and `prompts/INDEPENDENT_SESSION.md` before making changes. `prompts/PARALLEL_AGENTS.md` is the older multi-Agent coordination template; independent ChatGPT sessions must use the new protocol.

1. **ONLY repository:** `sstxww/reinforcement-learning`. It is a separate repository. Do not fork-push,
   modify, open PRs against, or write to `MCG-NJU/AutoTavern` or `rizling.top` source.
2. **Isolated branches:** each independent ChatGPT session generates a **globally unique** `agent-id`, uses `agent/<agent-id>/<task>`, and PRs to `main`.
   No Agent directly pushes to `main` or force-pushes another Agent's branch.
3. **Single owner per module:** inspect open PRs and choose a non-overlapping file set before changes.
   Shared files (workflows, API contracts, README) require integration-owner review.
4. **Mandatory battle:** run `python -m tavern_ai.canary --agent-id <agent-id>
   --seed <seed> --policy baseline --receipt experiments/<agent-id>/<experiment>.json`
   or `--policy model --model <path>`. This is a **full eight-seat TavernGym match**,
   not a few actions, not TavernBench, and not a fake result. Commit the JSON receipt.
5. **Hard gate:** a PR is eligible only after unit tests, a complete eight-seat match,
   receipt validation, and GitHub CI full-match gate pass.
6. **Reproducibility:** keep an exact upstream commit, patch SHA256, source hash, dataset
   version, seeds, total training steps, metrics and action-mask tests.
7. **No secret exposure:** never write `ARENA_API_KEY` or credentials to Git, URLs,
   command-line arguments, logs, artifacts, or comments. No model upload to Arena.
8. **No real ranked play without explicit user authorization.** Default to local
   TavernGym games. Arena `practice` is optional after approval; ranked modes
   `arena` and `standard` always require approval specifying number of games.
9. **No unsupported claims:** do not assert one model is stronger from a single win.
   Compare fixed independent seeds and report sample count and uncertainty.
10. **Integration:** PRs can be merged into main only by repository owner/integrator
    after checks. Never automatically merge conflicting experiments.

If tools or the simulator are unavailable, do not fabricate a receipt. Explain the
blocker in the PR and leave it unmerged. Every Agent must actually play its own match.
11. **Persistent research handoff:** each session must write `research/sessions/<agent-id>/round-<NNN>.md`, `STATUS.md` and a unique `research/knowledge/proposals/<agent-id>-<NNN>.md` in its own branch; curated `research/knowledge/` is integrator-owned.
12. **Isolated training:** the shared `train.yml` is main-only; do not use it as a private parallel run or overwrite another session's checkpoints/artifacts. Use a distinct finite workflow or isolated executor.
