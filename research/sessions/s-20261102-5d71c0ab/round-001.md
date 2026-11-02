# Round 001 — P0/P1 integration and P2 no-BUY diagnosis

Session: `s-20261102-5d71c0ab`. Own branch: `agent/s-20261102-5d71c0ab/optimization-001`. Start main SHA: `1afd8297e3c661bee3117ac5301b1ca08d64869b`.

## P0 real state
Initial audit: 75 open PR, 74 Draft, sole non-Draft #15 is stacked on Draft #9 and targets its branch. No PR was merged without passing safety/dependency gates. Several overlapping checkpoint/telemetry drafts already exist; main is changing concurrently.

## P1 actual source change and evidence
Hardened the EXISTING `tavern_ai/model_registry.py` Champion validator: `verified` label alone is inadequate, require literal true for durable download, SHA, load, optimizer resume, complete match, competitive gain. Population and Rejected reference validation also added. Synthetic regression tests passed in [dedicated run 41449729015](https://github.com/sstxww/reinforcement-learning/actions/runs/41449729015), no champion designated. GitHub Release real 1,408-step checkpoint was re-downloaded, digest matched, CPU load and one mask-legal inference passed; optimizer continuation from this specific downloaded tag remains **untested**.

## P2 authentic new evidence
Owned baseline match (one full 8-seat simulated game), seed **884631**, place **8**, `Game.is_over=true`, `placements=[8,2,5,3,4,7,1,6]`, turns 15, 37 decisions. Real receipt `experiments/s-20261102-5d71c0ab/001-884631.json` from successful GitHub Action.

New independent held-out seeds **884632/884633**, `v5-s-20261102-68099929-1408-41428692617` model SHA `a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632`:
- Pure model rank **[8,8]**, mask-legal BUY decision exposures **82**, BUY chosen **0**, model decision total **249**, actions ID1 **85** and ID2 **140**, no guard forced-ends.
- Same seeds Baseline rank **[6,7]**, exposures **49**, BUY **33**, model minus baseline mean placement **+1.5** (larger is worse).
- Not all legal BUY exposures are independent or good buys; rank comparison n=2 does not prove significance. Engine semantics and action-induced public state progression need separate verification before causal fix.

Source run and time-bounded artifact: https://github.com/sstxww/reinforcement-learning/actions/runs/41449729015/artifacts/13143652738. Compact permanent structured report: `reports/s-20261102-5d71c0ab/001-model-evidence.json`.

## Workflow format fix
Initial audit artifact `checkpoint-preflight.json` had printed environment-wrapping lines before valid JSON; the command did exit successfully, but machine-readable artifact was not clean. Replaced redirection with pipefail + final-line extraction + `json.tool` parse validation. Requires a new run of this branch to validate.

## Evaluation and training conclusion
No new PPO steps: **0**. No Champion/Best promotion. No official Arena. Repeated real no-BUY despite legal opportunities is robust enough to prioritize code-level action mapping, per-action state-delta telemetry, and a single-variable controlled intervention before training scale. Do not force-BUY blindly; other existing PRs have negative forced-BUY outcomes.

## Integration next gate
Recheck PR #118 exact final-head CI after this commit and recheck main's current head. If green and conflicts absent, have integration owner review and merge with exact-head SHA; post-merge main CI must also pass. If concurrent integration claims cannot be safely held, leave PR open rather than racing main.
