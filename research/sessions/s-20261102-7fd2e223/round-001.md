# Round 001 · s-20261102-7fd2e223 — verified exploratory negative/uncertain result

## Provenance
- Session: `s-20261102-7fd2e223`
- Branch: `agent/s-20261102-7fd2e223/optimization-001`
- Base main SHA: `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`
- Initial implementation SHA: `1051701249f6652605ab9a914c4f65e457961d7e`
- Initial real-match receipt commit: `7e85bc0dbcb8cd0bf9dcd98a4592f6cee9750017`
- Heldout workflow commit: `edb1a8ec3254ef5f6da9435c45f3404b79960528`
- Heldout receipt commit: `991fc948edbceba4012b1162eaf1a76e6309b4ac`
- Review PR: https://github.com/sstxww/reinforcement-learning/pull/36 (draft; do not promote to Best)
- Actions first: https://github.com/sstxww/reinforcement-learning/actions/runs/41415621730 (success)
- Actions independent heldout: https://github.com/sstxww/reinforcement-learning/actions/runs/41415938774 (success)

## Single hypothesis and method
The untouched V0 `BaselinePolicy` never selects a hero power in the normal idle state. Candidate `IdleHeroPowerPolicy` uses the first legal action 4/5 only when the control would end turn (action 0), at most once in one turn, and not after 60 actions that turn. The exact TavernGym legal mask is enforced again before `Game.step`; there is no fallback fake game. No shared baseline, PPO, common training/evaluation module, or other session data was modified.

All 12 fixed seeds (73101–73112) were paired between seat-0 policy candidate and the original control, with the other seven seats as the pinned TavernGym official rule bots. Each of the 24 executions reached `Game.is_over()`, produced eight final placement entries, and passed `validate_receipt`. There were no invalid actions, no truncated combats, no simulator turn-limit termination. Code regressions: **22 tests passed** in both Actions runs.

## Real measured outcomes

| Cohort | n pairs | Control ranks | Candidate ranks | Control mean | Candidate mean | Delta (candidate-control) | Hero-power actions |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| Pilot 73101–73104 | 4 | 7,7,8,7 | 4,5,5,7 | 7.250 | 5.250 | -2.000 | 26 |
| New heldout 73105–73112 | 8 | 7,7,5,8,6,6,7,6 | 7,7,5,8,6,6,7,7 | 6.500 | 6.625 | +0.125 | 19 |
| Combined | 12 | see records | see records | 6.750 | 6.167 | -0.583 | 45 |

Across 12 pairs: candidate improved 3 seeds, worsened 1, tied 8. Candidate top-four 1/12 (8.33%) versus control 0/12; **both first-place 0/12**. Bootstrap 95% interval for the paired mean difference, computed from the 12 real per-seed differences with a fixed random seed and 200,000 resamples, is approximately **[-1.33, +0.08]** (descriptive only). These samples are small, and the apparent pilot advantage did **not replicate in the independent heldout cohort**. **Not a confirmed strength gain; do not merge as a production strategy upgrade.**

## Mandatory own full eight-seat game
- Candidate receipt: `experiments/s-20261102-7fd2e223/001-73101.json`
- Genuine engine and game completion: `TavernGym 1.1.0`, `completed=true`, seat-0 placement 4, placements `[4,6,3,1,7,5,2,8]`
- Seed `73101`, controlled decisions `60`, turn `15`, legal-mask violations `0`, truncated combats `0`, turn-limit flag `false`
- Model hash: null (strategy-only); script implementing candidate in `tavern_ai/hero_power_probe_7fd2e223.py` at initial SHA above
- Run URL: https://github.com/sstxww/reinforcement-learning/actions/runs/41415621730
- Remaining 11 candidate receipts: `experiments/s-20261102-7fd2e223/001-<seed>.json`
- All 12 baseline receipts: `experiments/s-20261102-7fd2e223/001-control-<seed>.json`

## Engine / checkpoint / budget
- Simulator upstream read-only commit `fb61201a557ddd36a411cf44aac51ce4d9b606ce`
- Independent patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`
- Engine hash `6d8712c93022ba11`, feature dimension 4017, card IDs 447, action mask size 245, catalog pinned by `contract.py`
- Genuine strategy-only testing; **PPO training steps 0**, weights absent, checkpoint absent, no model to resume.
- Two bounded branch-only Actions workflows; 65-minute maximum per job, no repeated failed SHA and no Actions push-commit infinite trigger.
- JSON evidence is committed under this session's private namespace; temporary workflow artifact backup expires after 30 days, not a model backup.
- Failure reports: no failure encountered in this session. Other agents' PPO safety-cap and Release-403 incidents were reviewed but not claimed as repaired here.

## Interpretation / next hypothesis
The candidate passes the real-engine legality/completion gate but the heldout result does not support promoting idle hero-power usage as a general baseline rule. Avoid repeating this single unconditional heuristic. A subsequent independent round could stratify hero-power effects by actual hero identity, power cost, and current resources before choosing a targeted policy; require new heldout seeds and separate isolated files. Do not deploy to ranked TavernArena without explicit additional permission.
