# Failure 001 — authentic V2 raw model does not finish turn 1

Session: s-20261102-6b4eaf12
Source: GitHub Actions [41428090604](https://github.com/sstxww/reinforcement-learning/actions/runs/41428090604), job 125219503712, direct live logs.

## Verified positive checks
- Installed exact pinned TavernGym 1.1.0 (source hash 6d8712c93022ba11), unit suite passed.
- Downloaded existing GitHub Release `v2-learning-41413557445` from the real Release service.
- Checked `model.zip` SHA256 against 73bde2666426cecce39f135980a897bb2cd4a7d70783ba04c9c0d29477a6664a.
- Verified actual archived schema-2 metadata and ZIP optimizer member.
- Trusted `MaskablePPO.load` reports 1280 saved steps and legal model inference (initial action ID 30).

## Authentic behavioral failure (not a fake rank)
- Real complete-engine attempt seed 88132 with unmodified V2 model and no forced END guard.
- On **turn 1**, controlled seat exceeded **120 raw actions** without finishing turn; watchdog raised `RuntimeError: Raw model exceeded 120 actions in turn 1; no forced END`.
- Therefore **Game.is_over was not achieved**, no valid 8-seat receipt or placement exists for this run.
- This is not an installation, checksum, deserialization or mask-legal inference failure. A model can produce legal actions while being strategically/operationally stuck.
- Action ID types, exact repeated streak, and how often BUY was legally available were not captured in this original crash. Those must be measured before claiming the loop mechanism or advising action bias.

## Controlled repair / independent test
- One meaningful instrumentation fix separates two modes:
  1. Original **raw** model: run to a finite 120-decision-per-turn cap, persist `completed=false` trace with action histograms, legal purchase/play opportunities, same-action streak and identical-public-state counts. Never emit a full-match receipt when aborted.
  2. **Guarded** model: explicitly force a mask-legal END after 30 actions per turn, track `guard_forced_ends` and assess authentic full-game rank vs same-seed baseline, labelled as guarded. Not raw V2 strength.
- Dedicated workflow [41428940159](https://github.com/sstxww/reinforcement-learning/actions/runs/41428940159) scheduled to test this version; results pending live status.
- Neither workflow retries indefinite loops; all runs time-bounded. Original experimental PPO training steps in this session: **0**. No weights/Champion modified.

## Hypotheses (unconfirmed)
- Repeated option/free action may be legal yet zero-progress, or the policy may optimize a sparse reward without strategic buy/board development.
- Prior PR #60 independently observed low-LR candidate buying zero times across three completed games, but engine-legal buying opportunities were not measured.
- Need raw observation/mask/action-conditioned telemetry before changing reward/shaping or expanding PPO steps.

## Provenance and next gate
Latest main independently integrated four candidate Release records; this session reconciled its own duplicate registry to that existing model history, without overwriting it. Production promotion remains blocked on independent full-game, paired seeds, model reloaded and durable checks.
