# Round 001 — End-of-turn shop Freeze ablation

## Hypothesis and motivation
The main baseline never uses `Freeze` (upstream flat action ID 2). Test whether one legal Freeze before EndTurn on turns 4–9 when buying and refreshing are impossible improves placement. This changes only session-owned policy code, not shared policy. The freeze is at most once per turn to avoid toggle loops.

## Reviewed evidence and provenance
Main SHA `315b068bac5ab6d8403c3c9b18f8c101c0cded5d`. Read AGENTS.md, PROJECT_BACKGROUND, ARCHITECTURE, SESSION_PROTOCOL, CLOSED_LOOP, knowledge incidents, active PRs and Actions. Upstream `fb61201a557ddd36a411cf44aac51ce4d9b606ce`, pinned patch SHA256 `1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0`, expected source hash `6d8712c93022ba11`. Observations 4017 float, 447 cards; 245 masked actions.

## Method
- Paired real-game seeds 29101–29110, one candidate seat 0 versus seven official bots and one baseline seat 0 versus seven bots per seed.
- Game ends only if `Game.is_over()`; failed games produce no fake successful receipt.
- Use independent workflow with 65-minute limit, one initial push trigger and no automatic rerun on receipt-only commits.
- No PPO training, model weights, or formal strength claim from small N.

## Actual execution
Pending GitHub Actions and receipt verification. See `metrics-001.json` and workflow logs once execution succeeds; unobserved outcomes must not be inferred.

## Next hypothesis
If freezing is not robust across independent seeds, test a public-observation-driven conditional shop value filter; do not modify shared baseline without independent evidence.
