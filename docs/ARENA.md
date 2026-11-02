# TavernArena adapter — manual authorization only

Before joining, check https://rizling.top/agent.md, https://rizling.top/protocol, and the current https://rizling.top/api/v1/manifest against the pinned engine version, source hash, and card vocabulary.

Download and review https://rizling.top/downloads/client.py as `arena_client.py` in your private runner. Keep `ARENA_API_KEY` in an environment variable or Actions secret; never expose it in a URL, command, code, or logs. Set `TAVERN_AI_MODEL` to a compatible trained checkpoint.

Contract inspection:
```bash
python arena_client.py --url https://rizling.top --check
```
Non-ranked practice only after explicit permission:
```bash
python arena_client.py --url https://rizling.top --policy tavern_ai.arena_policy:act --mode practice
```
Ranked modes `arena` or `standard` require separate authorization, including number of games. No credentials are necessary for local TavernGym simulation. Public match results are not complete opponent trajectories or training data.
