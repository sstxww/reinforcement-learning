"""Real-game, public-observation buy-opportunity diagnosis for model rank-eight.

No reward or policy intervention, no forced end-turn. A legally masked BUY is
counted as a chance even if the model chooses something else. This deliberately
does NOT assume that a missing BUY means an available opportunity was missed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import FEATURES, CARDS, ACTIONS, verify_engine
from .validate_receipt import validate


def classify(action: int) -> str:
    if action == 0:
        return "end_turn"
    if 8 <= action <= 15:
        return "buy"
    if 16 <= action <= 22:
        return "sell"
    if action == 3:
        return "upgrade"
    if action == 1:
        return "reroll"
    if 30 <= action < 46:
        return "choose"
    if 46 <= action < 126:
        return "play"
    return "other"


def summary_from_decisions(events: list[dict]) -> dict:
    if not events:
        raise ValueError("No real recorded model decisions")
    counter: Counter[str] = Counter()
    distinct_buy_turns: set[int] = set()
    missed_buy_turns: set[int] = set()
    unique_legal_buy_states: set[str] = set()
    for e in events:
        action = e["action"]
        legal = e["buy_legal"]
        turn = e["turn"]
        if type(action) is not int or type(legal) is not bool or type(turn) is not int or turn < 0:
            raise ValueError("Invalid action opportunity record")
        counter[classify(action)] += 1
        if legal:
            counter["buy_legal_decisions"] += 1
            distinct_buy_turns.add(turn)
            unique_legal_buy_states.add(e["state_hash"])
            if action == 0:
                counter["end_while_buy_legal"] += 1
                missed_buy_turns.add(turn)
        if action == 0:
            counter["all_end_turns"] += 1
        if e.get("same_public_state_as_prior") is True:
            counter["consecutive_identical_public_observation"] += 1
    return {
        "decisions": len(events), "by_action_family": dict(counter),
        "buy_legal_decisions": counter["buy_legal_decisions"],
        "distinct_turns_with_legal_buy": len(distinct_buy_turns),
        "unique_public_states_with_legal_buy": len(unique_legal_buy_states),
        "end_while_buy_legal": counter["end_while_buy_legal"],
        "turns_with_end_while_buy_legal": len(missed_buy_turns),
        "buy_chosen": counter["buy"], "all_end_turns": counter["all_end_turns"],
        "consecutive_identical_public_observation": counter["consecutive_identical_public_observation"],
        "conditional_buy_rate_given_legal": counter["buy"] / counter["buy_legal_decisions"] if counter["buy_legal_decisions"] else None,
        "conditional_end_rate_given_legal_buy": counter["end_while_buy_legal"] / counter["buy_legal_decisions"] if counter["buy_legal_decisions"] else None,
        "caveat": "Every masked BUY is legal; action-level opportunities are temporally dependent. Not all missed legal BUY actions are mistakes."
    }


def real_trace(seed: int, agent_id: str, policy: str, model_path: Path | None) -> dict:
    import taverngym
    if policy not in {"model", "baseline"}:
        raise ValueError("Only genuine baseline or model is supported")
    if not agent_id or any(ch in agent_id for ch in "/\\"):
        raise ValueError("Invalid session ID")
    engine = verify_engine()
    policy_model = None
    model_sha = None
    if policy == "model":
        if model_path is None or not model_path.is_file():
            raise FileNotFoundError("Must provide actual model bytes")
        from sb3_contrib import MaskablePPO
        model_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
        policy_model = MaskablePPO.load(str(model_path), device="cpu")
    baseline = BaselinePolicy()
    game = taverngym.Game(seed=seed)
    last_turn, decisions_used, decisions, last_state_hash = -1, 0, 0, None
    events: list[dict] = []
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, decisions_used, last_state_hash = turn, 0, None
        progress = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progress = True
            if seat != 0:
                game.bot_play(seat)
                continue
            f, c = game.observe2(0)
            features = np.frombuffer(f, dtype="<f4").copy()
            cards = np.frombuffer(c, dtype="<i4").copy()
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if (features.shape, cards.shape, mask.shape) != ((FEATURES,), (CARDS,), (ACTIONS,)):
                raise ValueError("Unexpected pinned observe2 dimensions")
            if not mask.any() or not np.isfinite(features).all():
                raise ValueError("Malformed legal mask or observation")
            buy_legal = bool(mask[8:16].any())
            state_hash = hashlib.sha256(features.tobytes() + cards.tobytes() + mask.tobytes()).hexdigest()[:24]
            if policy_model is not None:
                action, _ = policy_model.predict({"features": features, "cards": cards}, action_masks=mask, deterministic=True)
                action = int(np.asarray(action).item())
            else:
                action = baseline.act({"features": features, "cards": cards, "action_mask": mask},
                                      {"turn": turn, "actions_used": decisions_used})
            if not mask[action]:
                raise ValueError("Illegal policy action")
            # First-party public UI field 33 is verified as own-board count by
            # independent public observation tests; use for descriptive telemetry.
            board_size = int(round(float(features[33])))
            events.append({
                "turn": turn, "action": action, "family": classify(action),
                "buy_legal": buy_legal, "legal_buy_count": int(mask[8:16].sum()),
                "board_size": board_size,
                "state_hash": state_hash,
                "same_public_state_as_prior": state_hash == last_state_hash,
            })
            game.step(0, action)
            decisions_used += 1
            decisions += 1
            last_state_hash = state_hash
            if decisions_used > 250:
                raise RuntimeError("Too many actions in one turn; no full-match receipt fabricated")
        if not progress and not game.is_over():
            raise RuntimeError("Genuine TavernGym game stalled")
    if not game.is_over():
        raise RuntimeError("Genuine TavernGym game did not finish under bounded steps")
    result = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"], "agent_id": agent_id,
        "policy": policy, "model_sha256": model_sha,
        "seed": seed, "completed": True, "turns": int(game.turn),
        "decisions": decisions, "placements": [int(x) for x in game.placements()],
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end), "git_sha": os.getenv("GITHUB_SHA", ""),
        "opportunity_summary": summary_from_decisions(events),
        "trace_first_32": events[:32],
        "model_guard_forced_end": 0,
        "public_observation_only": True,
    }
    validate(result)
    if sorted(result["placements"]) != list(range(1,9)):
        raise ValueError("Invalid permutation of eight ranks")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--policy", choices=("model", "baseline"), required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = real_trace(args.seed, args.agent_id, args.policy, args.model)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "seed": args.seed, "policy": args.policy, "rank": receipt["placements"][0],
        "opportunity_summary": receipt["opportunity_summary"]
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
