# Round 001 — shop refresh when no buy is legal (negative feasibility pilot)

## Identity and hypothesis
- Session ID: `s-20261102-6cc5d763`.
- Branch: `agent/s-20261102-6cc5d763/optimization-001`.
- Main baseline SHA: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`.
- Hypothesis: one legal Refresh action when Baseline would EndTurn and no Buy is legal will improve placement.
- Source of idea: original baseline never selects action 1 Refresh; pinned upstream `actions.rs` confirms 0=EndTurn, 1=Refresh and 8..16=Buy. Previous failure notes warn about PPO action loops.
- Scope: brand-new `tavern_ai/refresh_ablation.py`, one test module, one isolated workflow, own receipts/notes only. No shared baseline or PPO changes.

## Actual execution and configuration
- Successful run: https://github.com/sstxww/reinforcement-learning/actions/runs/41415018609 (job 125176644550), code SHA `d1eed5699186a265d8c704bb7eaea917dec29535`.
- Real TavernGym 1.1.0, source hash `6d8712c93022ba11`, observe2 4017 floating features / 447 card indices / 245 legal-masked actions.
- Rule tuning only: PPO training steps **0**, no model/checkpoint, no candidate model weight hash.
- Candidate policy hash SHA256 `e2f8d2f8d23b56489eef9de8f86b815fc468dd914f256ac84ab02a9809f64c36`.
- The mask gates every action; maximum one refresh per turn, no refresh before turn 3, no refresh if Buy is legal, and no refresh after >=80 actions in a turn.
- Test/dependency, pinned engine installation, seven complete games, receipt validation, evidence commit and Artifact upload: all workflow steps passed.
- Mandatory independent candidate game: seed 36501, `Game.is_over()==True`, seat 0 rank **8**, 45 decisions, 15 turns, all placements `[8,6,2,4,7,3,1,5]`, no truncated combat or protective turn limit; receipt `experiments/s-20261102-6cc5d763/001-36501.json`.
- Other seven seats were native TavernGym scripted bots. No official TavernArena matches.

## Independent paired evaluation
- Held-out seeds: 36502, 36503, 36504.
- Baseline ranks `[8,8,8]` (3 games), candidate ranks `[8,8,8]` (3 games).
- Both mean placement 8.0, first place 0%, top-four 0%. Paired rank deltas candidate-minus-control `[0,0,0]`.
- Crucial: **Refresh activation count 0 for the mandatory game and 0 for all three held-out candidate games**. This pilot is a feasibility failure: the extra branch was not taken. The zero rank delta is not evidence that using Refresh is strategically ineffective.
- Actual compact report `reports/s-20261102-6cc5d763/comparison.json`, per-game committed receipts `experiments/s-20261102-6cc5d763/`, generated solely by the real engine.
- All four candidate games completed; no illegal action; failed hypothesis due to non-activation rather than simulator failure. With n=3, no strength assertion is appropriate.

## Artifacts, reproducibility, prior learning
- Artifact ID 13127905152, `refresh-s-20261102-6cc5d763-41415018609`; expires 2026-12-02 08:44:26 UTC. Results and receipts are committed, no checkpoint exists for this strategy-only experiment.
- Rerun only as a deliberate new hypothesis using `python -m tavern_ai.refresh_ablation --seed 36501 --start-seed 36502 --games 3` after installing pinned engine. Do not blindly rerun identical seed and code.
- Historical PR #15 shows 1280 PPO steps without rank gain; PR #11's first four placement games appeared stronger but 16 new seeds invalidated the apparent improvement. This motivated independent seeds and conservative claims.
- No temporary raw rollouts or model weights saved. No known permission incident in this run.
- Next distinct hypothesis: try at most one refresh **before an otherwise legal purchase** on later turns when Refresh and Buy are simultaneously legal, then compare on fresh seeds and count actual interventions. Do not promote a strategy without activation and statistical evaluation.

## Final gate
- This session's Actions experiment succeeded. [Draft PR #27](https://github.com/sstxww/reinforcement-learning/pull/27) was created. PR CI [41415522281](https://github.com/sstxww/reinforcement-learning/actions/runs/41415522281) passed on `ea1ffaa11fa4f618a9a1a72f36e4f1e01e55ed5f`; check the latest documentation-only commit CI before declaring final head green.
