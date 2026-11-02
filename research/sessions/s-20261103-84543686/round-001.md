# Round 001 — actual P0 PR review and bounded P2 diagnostic

**Session** `s-20261103-84543686`; **Role** WORKER; **Base** `3602f64b798bb51dcf69ef5964fe0b4c4cd39495`; **Claim key** `p0/p1-pr161-pr164-integration-review-and-p2-seed99407`.

## Independent live review
- Inspected `main` trainer, SHA-bound checkpoint writer, schema-2 archive preflight, Release-backed main train workflow, registry, and the actual #161/#164 diffs.
- Main currently **ignores** `verify_resume_digest(...)` returning False for metadata without a checkpoint SHA; [#161 review](https://github.com/sstxww/reinforcement-learning/pull/161#pullrequestreview-5742124665) explains fail-closed candidate and gate.
- Main currently overwrites schema-2 parent model provenance with schema-1 after learning; [#164 review](https://github.com/sstxww/reinforcement-learning/pull/164#pullrequestreview-5742125132) identifies candidate remedy and the same-file conflict. Do not merge both blindly; do not misattribute others' work.
- Existing #117/#125/#116/#138/#154/#162 merges were performed by **other** sessions. #15 is non-Draft but stacked on Draft #9. Here: **zero merges**.

## Falsifiable P2 experiment
- Hypothesis: the original raw 1408-step PPO at known SHA still has a conditioned BUY-selection deficit on a fresh seed even when the legal mask offers BUY. This tests the reproducibility of symptoms, **not** why PPO prefers FREEZE/REFRESH.
- Pin original Release digest and engine contract. Pre-register **seed=99407 and controlled seat 0** for both baseline and **unguarded model**, seven script opponents. Capture original complete eight-seat receipts and public BUY-mask exposure if games genuinely finish.
- Bounded Actions workflow: once per owned branch workflow creation; CPU, 65-minute hard timeout, two engine games max, no PPO update, no writing or promoted model. The baseline game is **infrastructure-only** and must not be represented as a model win.
- Until actual original outputs are inspected, own games = **0 verified**, own PPO added steps **0**, persistent model = **none**. Existing Release is read-only shared baseline.

## Follow-up gate
Review Actions run result; if any model run exceeds safety bounds, save failure without placement. Compare only same-seed completed games. Preserve work as Draft if no own receipt; no direct main or other-agent edits; any strategic improvement requires real paired replication before training expansion.

## R001 authentic match result and independently restored evidence
- GitHub Actions `41510235754` **success**, original Artifact `13171803636` downloaded. SHA-pinned Release file passed `sha256sum --check`. Pinned TavernGym 1.1.0 / observe2 4017,447,245 / source `6d8712c93022ba11`.
- Same seed 99407, same controlled seat 0 and seven scripted opponents: baseline complete [8,2,1,7,4,5,3,6], 36 decisions, 15 turns; *unguarded raw* 1408-step PPO complete [8,7,1,6,2,4,3,5], 125 decisions, 15 turns. Neither improves own placement. Model 1 BUY / 49 mask-legal exposures over 7 turns, 43 REFRESH, 70 FREEZE ID2, 1 PLAY; zero guard intervention. Raw mask exposure count is correlated and does not establish optimal purchases or unique fault.
- Original baseline/raw JSON SHA256 `2a293501926790dd1d23564262cd3906a92b338783707eac7b4f0428d4883626`/`ecf009256faea66c24c0678fed5fa25e0544a59a8ec074647ed51ccf6454937c`. The repository JSON copies are reformatted semantic equivalents; original bytes remain in the temporary Artifact. Raw public trace covers first 32 decisions, **not** all 125. Training delta 0, no model promotion.
- Early PR CI [41510317526](https://github.com/sstxww/reinforcement-learning/actions/runs/41510317526) passed all Python unit tests (337 passed, 1 skipped) then failed due to missing receipt before the Actions experiment completed. Actual receipt is now included on new head, pending fresh CI. #161 merged by another session; main latest observed `70c411b...`.
