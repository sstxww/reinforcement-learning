# Rank-eight root-cause cross-evidence audit — s-20261102-5a69c4f2 R001

> This is a **read-only synthesis of existing genuine GitHub receipts and
> independently labeled draft evidence**, not an additional match or new PPO training.
> Do not promote any candidate on this report.

## Provenanced evidence

**Main-merged observation A: 1408-step Challenger, same-seed 99128.**
Source: [reports/s-20261102-68099929/003-buy-opportunity.json](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-68099929/003-buy-opportunity.json).
The model made 117 decisions; a BUY action was mask-legal on 35
decision points across 7 turns; the model selected BUY **0** times.
It selected 37 REROLL actions and finished rank 8, with **zero
forced-end guard events**. The baseline had 21 BUY-legal decision points,
selected BUY 14 times, also finished rank 8 in this single pair. Thus
one game proves a model-action failure but **does not** prove that
fixing purchase frequency alone improves placement.

**Main-merged observation B: V2 guarded model, seeds 87102 and 87103.**
Source: [reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-ba09e2d4/005-guarded-evaluation-summary.json)
and [turn traces](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-ba09e2d4/003-87102-guard-metrics.json).
Real guarded rank [8,8] vs paired baseline [5,7]. The model chose BUY
0 times despite 7 and 6 distinct turns with mask-legal BUY.
On 87102 it made 70 FREEZE, 37 REFRESH, 91 MOVE actions and required
4 explicit HeroPower/Cancel guard interventions; 87103 made 60 FREEZE
and 34 REFRESH, with no guard interventions. This independently supports
purchase neglect and low-value action concentration.
**Guarded results are not raw model strength.**

**Main-merged observation C: V2 model, seeds 45111 and 45112.**
Source: [reports/s-20261102-83d91476/001-buy-opportunity-report.json](https://github.com/sstxww/reinforcement-learning/blob/main/reports/s-20261102-83d91476/001-buy-opportunity-report.json).
In two full games the candidate had 74 decision-level BUY-legal exposures,
chose BUY 0 times, and chose raw action IDs 1/2 on 222 of 248 actions;
its ranks were [8,8] vs baseline [6,7]. The action-code semantics
require explicit contract checking; this observation alone does not prove
the absence of state progress.

**Independent draft evidence D, NOT main-integrated: PR #103.**
[PR #103](https://github.com/sstxww/reinforcement-learning/pull/103)
reports three complete eight-seat heldout seeds 89101–89103, V2
guarded ranks [8,8,8], 521 BUY-legal decision points and zero BUY;
12 forced EndTurn interventions. This supports external replication,
but the branch is a Draft with overlapping main code and dependencies,
so do not blindly merge it or substitute for main-owned evidence.

**Independent draft intervention E, NOT main-integrated: PR #107.**
[PR #107](https://github.com/sstxww/reinforcement-learning/pull/107),
stacked on #103, reports nine actual games on 89111–89113: unchanged
baseline, original guarded PPO and forced-mask-legal-BUY guarded PPO all
placed [8,8,8]. Forced-BUY policy made 46 real purchases across its
three games versus original guarded PPO's zero, but still rank 8;
it needed 18 forced EndTurns versus original's 1 and exhibited many
Play/Cancel cycles. Source [Actions 41429432385](https://github.com/sstxww/reinforcement-learning/actions/runs/41429432385).
This **falsifies the narrow hypothesis** that simply selecting the
first mask-legal BUY fixes rank-eight placement **on these three seeds**.
It does not prove purchases have zero long-run value. The experiment
uses a guard and has no PPO weight update.

## Root-cause decision

- **Confirmed for the tested checkpoints/seeds:** BUY was mask-legal
  in many observed states; selected BUY count was zero for the raw
  candidate on observed main-owned seeds. The policy's poor BUY
  utilization is not explained by the absence of available mask-legal
  BUY actions in those states.
- **Confirmed for observed traces:** excessive REFRESH/FREEZE and
  in some games MOVE/HeroPower-Cancel or Play-Cancel repetition consumes
  decisions. Guard interventions can make an otherwise stalled game
  complete without making the policy strong.
- **Evidence against a naive fix:** forced legal purchasing alone did
  not improve rank in three draft-branch paired seeds, while
  increasing loop/forced-EndTurn dependence.
- **Not established:** exact reward/advantage gradient failure,
  observation normalization bug, specific incorrect action-mask bit,
  precise point in the economy/board trajectory when deficits became
  irreversible, effects on unseen seeds, or a statistically supported
  competitive gain.

## Next falsifiable experiment (before expanding PPO)

Run matched independent seeds at fixed seat and rotated seats while
capturing **per-turn gold, purchases, hand/board size and stat delta**,
BUY legality by distinct states (not raw repeated decisions), action
transition pairs and count of no-state-progress decisions. Compare raw
PPO, already-merged opt-in loop guard, a **single** targeted loop
resolution/mandatory-choice intervention, and a rule baseline under
separately labeled safety policies. Cap raw games and report incomplete
ones as failures, never rank results. Only then consider a targeted
behavior-cloning/reward hypothesis and a bounded PPO smoke. No
Champion promotion until unguarded completion, Release recovery and
independent paired results are established.
