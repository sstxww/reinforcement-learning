# s-20261102-24728f13 · Session status

- **State:** completed experiment; draft PR under final-head CI review. No Best promotion.
- **Branch:** `agent/s-20261102-24728f13/optimization-001` (derived from main `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`).
- **PR:** https://github.com/sstxww/reinforcement-learning/pull/51
- **Main experiment:** https://github.com/sstxww/reinforcement-learning/actions/runs/41416467100 — success. 512 real PPO steps (256 per learning rate), six genuine eight-seat model-controlled games, all `Game.is_over()`, zero illegal/truncated/turn-limit issues.
- **Restore test:** https://github.com/sstxww/reinforcement-learning/actions/runs/41417110915 — success. Both SHA256s, CPU model reload and masked legal action confirmed.
- **CI:** PR #51 Actions for latest head SHA must be checked after final documentation changes.
- **TavernGym:** 1.1.0; source `6d8712c93022ba11`; observe2 4017 float / 447 cards / 245 actions.
- **Outcome:** candidate 1e-4 and reference 3e-4 each got [8,8,8], mean 8.0, top-four 0%, first-place 0% (three seeds per arm). **No verified competitive gain**. No promoted Best model in this session.
- **Real receipt:** `experiments/s-20261102-24728f13/001-42171.json`; all other receipts in same directory.
- **Metrics:** `reports/s-20261102-24728f13/001-lr-ablation.json`.
- **Recovery evidence:** `reports/s-20261102-24728f13/001-checkpoint-recovery.json`.
- **Model restoration:** download Artifact ID `13128665279` from run 41416467100, restore `outputs/s-20261102-24728f13/candidate.zip` (SHA256 `802c65e7da2ba42e26e2f2efb55859b91428f1b792428031947484ce95f42f18`) or `reference.zip` (SHA256 `8450905bdd1d78e6be68175f9943b16ac840fc9ce2882da4e32791ddb078ad0c`); install project + pinned TavernGym, verify source compatibility and hashes before load. Artifact expires December 2, 2026. No permanent storage claim.
- **Outstanding:** action-quality telemetry; small evaluation n; need durable non-expiring checkpoint storage if prolonged continuation is desired. No own open failures; all historical failure hypotheses require separate verification.
- **Next round hypothesis:** early end-turn/low economic investment—not learning rate alone—limits these short-run policies; capture decisions and per-turn action breakdown in an isolated seeded probe.
