# R002 — independent no-retuning replication of R001 sell-swap

- SESSION_ID s-20261102-1692601b
- Branch agent/s-20261102-1692601b/optimization-002, derived ONLY from own Round 001 head 534a316970464937e883209a89321e924af87a3c.
- Dependency: own draft PR #72. R002 PR must not be merged before R001 review.
- Rules: pinned TavernGym 1.1.0 hash 6d8712c93022ba11; our game mechanism is Sell 16..22, Buy 8..15; only public observable mask and turn fed to candidate.
- R001 weak evidence: 4 heldout pairs, mean rank delta -0.25 (3 ties, one candidate rank gain). No top4 gain.
- HYPOTHESIS: the chosen parameters turn>=7 and first sale slot may generalize beyond selection seeds. Counter-hypothesis: small pilot's favorable result is noise.
- FIXED before test: seeds 69131..69150 (20 heldout pairs), seat i%8, original baseline vs unchanged candidate on same seed/seat; 40 real complete eight-player games.
- Tests: verify seat-specific rank attribution, nonoverlapping seeds and exact sign/bootstrapped uncertainty.
- No fitting, tuning, PPO or gradient training in R002. R001 had 10 actual calibration games. No new neural model or checkpoint.
- R002 result: PENDING actual workflow. Save 002-*.json receipts and metrics-002.json; never invent outcomes.
