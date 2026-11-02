# V5 s-20261103-630ed53f R001 — P0 integration and P2 masked BUY-probability diagnostic

Session: s-20261103-630ed53f. Branch: agent/s-20261103-630ed53f/optimization-001. Starting main HEAD: e837e7b445cfb74a84fdb871a4bae4ec9e0ce034 (#117 manual registered Release restore). No upstream, user computer, or ranked Arena changes.

## P0 actual review
At initial inspection: 115 open PRs, 111 Draft. PR #15 is stacked on Draft #9. Exact HEAD of #116/#130/#154 had successful CI but main moved during guarded #154 premerge recheck, so this session did NOT merge #154; peers later merged #116 and #154 and verified main CI.
Posted source-specific duplicate-verifier blocking review on PR #130: https://github.com/sstxww/reinforcement-learning/pull/130#issuecomment-6586054524. Main #116 already uses strict checkpoint_preflight for ZIP/CRC/optimizer/schema.
Posted production default-restoration defect review on PR #149: https://github.com/sstxww/reinforcement-learning/pull/149#issuecomment-6586103758. Subsequent #117 merge changed main to manual-only, fail-closed registered Release recovery, so review #149 again against NEW main.
Other agents merged #125 SHA-bound checkpoint staging and independently ran short PPO resumes; their operations are not ours.

## P2 falsifiable question
An authentic V5 1408-step raw-model seed 99231 game was eighth: 38 mask-legal BUY decision exposures, zero BUY, 42 REFRESH and 70 FREEZE without fallback. Same-seed baseline was also eighth. A separate Draft #107 forced 46 buys across three guarded games with no rank improvement and Play/Cancel cycles. These are observations, NOT root-cause proof.
This round measures masked PPO probability mass for BUY action IDs 8..15 versus REFRESH/FREEZE IDs 1..2 at each legal-buy state, plus selected action, entropy, and repeated public decisions. It does not change actions or train. Existing Draft #150 addresses public state deltas and guarded V2 games rather than raw V5 action probabilities.

## Reproducible independent gate (pending)
TavernGym 1.1.0 pinned engine hash 6d8712c93022ba11; observe2 floats 4017, cards 447, actions 245.
Model unpromoted 1408-step Release: v5-s-20261102-68099929-1408-41428692617; expected SHA256 a73d24c68d238396136c9857ec4f341f39afc6562139ce9b693d282019db2632. Download immutable weights/metadata and run archive preflight + actual CPU inference.
Own new eight-player seed 99631: baseline and raw-model official canary; own bounded distribution probe with explicit completed/incomplete status. Official receipts only after source code actually generated and validate_receipt succeeded.
Workflow v5-action-probability-s-20261103-630ed53f.yml is independent, read-only, bounded, and triggered only once when the workflow file is first committed. Artifacts are temporary.
Own additional PPO steps: 0. Saved new weights: none. Champion: null. Competition improvement: unproven.

## Handoff
Read actual Actions run/jobs and artifact. Commit only genuine successful canary receipts; if run fails or is partial, mark blocked and retain diagnostic evidence. Do not scale PPO until recovery, rank-eight root cause and true-game gates. All claims should distinguish this session from other agents.
