# Round 001 — Play/Cancel observable-state cycle discriminator

## Inherited factual evidence
- Official registered 1408-step candidate is an unpromoted historical Release. No raw improvement established.
- Draft [#181](https://github.com/sstxww/reinforcement-learning/pull/181) recorded a true 1408→1536 resume and a bounded **incomplete** raw game with 2,782 Play and 2,775 Cancel out of 6,000 own decisions; that is a diagnostic, not a placement. Do **not** infer a unique causal root from action counts.
- [#182](https://github.com/sstxww/reinforcement-learning/issues/182) proved CAS coordination alone fails to exclude external merges.
- Current main at first inspection `c1b828734527bae6141805581693d890cc3bff94`, green [CI 41512315964](https://github.com/sstxww/reinforcement-learning/actions/runs/41512315964). Posted a concrete integration race review on [#185](https://github.com/sstxww/reinforcement-learning/pull/185#issuecomment-6586787126).

## Minimal falsifiable implementation
- Capture legal raw model action, before and after `observe2+legal_mask` SHA256 for the controlled seat and the current game turn.
- Adjacent Play(46–125)→Cancel(7) pairs are **patterns**, not automatically no-ops.
- Count an exact observable-state return only when after-Play equals before-Cancel AND before-Play equals after-Cancel; track recurring pairs in same turn. Reset at turn boundary and intervening unrelated actions. No opponent private state logged.
- Separate `legal_buy_decisions` from independent affordable purchase opportunities; do not equate them.
- A 384-model-decision cap makes an incomplete game a diagnostic with null placement, never an eight-seat receipt.
- Self-contained tests reject illegal masks, broken chain, cross-turn false loops, missing after-state, and validate same-public-state recurrence. Synthetic inputs are not a real-game result.

## Execution contract
- Own read-only bounded workflow only; exact Release downloaded through main's canonical `release_restore_entry`, SHA checked, pinned engine, baseline canary on seed 99831, raw policy probe on the same seed; artifact retention 30 days. No dispatch to formal ranked Arena.
- Actions, artifacts, seed, model SHA, complete status and errors must be recorded after **real** execution. No Release or raw-model strength claim before completed verified evidence.
- No PPO steps this round by design: existing raw behavior failures make a second unmotivated large training experiment counterproductive.
- Merge gateway P0 remains independently blocked by out-of-band API merge bypass; the unique task claim is not an integration lease.

## Next round
Inspect actual run and failure signature; if exact observable loops are absent, investigate change of public state rather than asserting a loop. If present, design single-variable intervention separate from raw. Preserve both outcomes. Rebase/verify own PR on latest main, obtain independent review and true serialized merge authority before integration.
