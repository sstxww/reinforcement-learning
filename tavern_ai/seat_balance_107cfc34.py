"""Isolated TavernGym eight-player seat-sensitivity probe (baseline V0).

Not an improved policy. This probes whether seat-0-only evaluation masks
variation due to seat, hero assignment and bot opponents.
"""
from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, verify_engine
from .validate_receipt import validate

def run_seat(seed: int, agent_id: str, seat: int) -> dict:
    if not 0 <= seat < 8:
        raise ValueError("seat must be 0..7")
    if not agent_id or "/" in agent_id or "\\" in agent_id:
        raise ValueError("invalid agent id")
    import taverngym
    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    decisions, last_turn, actions_this_turn = 0, -1, 0
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, actions_this_turn = turn, 0
        progressed = False
        for player in range(game.num_players):
            if not game.needs_action(player):
                continue
            progressed = True
            if player != seat:
                game.bot_play(player)
                continue
            fbytes, cbytes = game.observe2(seat)
            features = np.frombuffer(fbytes, dtype="<f4").copy()
            cards = np.frombuffer(cbytes, dtype="<i4").copy()
            legal = np.frombuffer(game.legal_mask(seat), dtype=np.uint8).astype(bool)
            if (features.shape, cards.shape, legal.shape) != ((FEATURES,), (CARDS,), (ACTIONS,)):
                raise ValueError("unexpected observe2 contract")
            action = baseline.act(
                {"features": features, "cards": cards, "action_mask": legal},
                {"turn": turn, "actions_used": actions_this_turn})
            if not legal[action]:
                raise ValueError(f"illegal baseline action {action} at seat {seat}")
            game.step(seat, int(action))
            decisions += 1
            actions_this_turn += 1
        if not progressed and not game.is_over():
            raise RuntimeError("game stalled")
    if not game.is_over():
        raise RuntimeError("full-game safety limit exceeded")
    placements = [int(x) for x in game.placements()]
    if sorted(placements) != list(range(1, 9)):
        raise ValueError("placements must be permutation of 1..8")
    result = {
        "schema": 1, "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_source_hash": engine["source_hash"],
        "engine_version": engine["version"], "agent_id": agent_id,
        "policy": "baseline-seat-probe", "seed": seed, "completed": True,
        "controlled_seat": seat, "controlled_placement": placements[seat],
        "turns": int(game.turn), "decisions": decisions,
        "placements": placements,
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "git_sha": os.getenv("GITHUB_SHA", ""), "model_sha256": None,
        "policy_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    validate(result)
    return result

def summarize(records: list[dict], seats: tuple[int, int] = (0, 1)) -> dict:
    if len(set(seats)) != 2 or any(not 0 <= s < 8 for s in seats):
        raise ValueError("two distinct seats are required")
    paired: dict[int, dict[int, int]] = {}
    for record in records:
        validate(record)
        seat = record.get("controlled_seat")
        if seat not in seats or record["controlled_placement"] != record["placements"][seat]:
            raise ValueError("controlled seat/placement mismatch")
        seed = record["seed"]
        if seat in paired.setdefault(seed, {}):
            raise ValueError("duplicate seat for seed")
        paired[seed][seat] = record["controlled_placement"]
    if not paired or any(set(v) != set(seats) for v in paired.values()):
        raise ValueError("missing seat in paired game")
    by_seat = {
        str(seat): {
            "games": len(paired),
            "mean_placement": sum(p[seat] for p in paired.values()) / len(paired),
            "first_place_rate": sum(p[seat] == 1 for p in paired.values()) / len(paired),
            "top4_rate": sum(p[seat] <= 4 for p in paired.values()) / len(paired),
            "placements_by_seed": {str(seed): p[seat] for seed, p in sorted(paired.items())}
        } for seat in seats
    }
    deltas = {str(seed): p[seats[1]] - p[seats[0]] for seed, p in sorted(paired.items())}
    return {
        "policy": "baseline-seat-probe", "seats": list(seats),
        "paired_seeds": sorted(paired), "total_games": len(records),
        "by_seat": by_seat,
        "paired_mean_delta_seat1_minus_seat0": sum(deltas.values()) / len(deltas),
        "paired_deltas_by_seed": deltas,
        "interpretation": "Descriptive only; hero assignment and scripted opponents also change with seat.",
        "competitive_strength_claim": "not established"}

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--agent-id", required=True)
    p.add_argument("--seeds", nargs="+", type=int, required=True)
    p.add_argument("--seats", nargs=2, type=int, default=[0, 1])
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--summary", type=Path, required=True)
    a = p.parse_args()
    if len(set(a.seeds)) != len(a.seeds) or len(set(a.seats)) != 2 or any(not 0 <= s < 8 for s in a.seats):
        p.error("seeds must be distinct and seats distinct within 0..7")
    records = []
    for seed in a.seeds:
        for seat in a.seats:
            receipt = run_seat(seed, a.agent_id, seat)
            fn = f"001-{seed}.json" if seat == a.seats[0] else f"001-{seed}-seat{seat}.json"
            a.out_dir.mkdir(parents=True, exist_ok=True)
            (a.out_dir / fn).write_text(json.dumps(receipt, indent=2), encoding="utf-8")
            print("SEAT_PROBE_RECEIPT=" + json.dumps(receipt, sort_keys=True), flush=True)
            records.append(receipt)
    summary = summarize(records, tuple(a.seats))
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("SEAT_PROBE_SUMMARY=" + json.dumps(summary, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()
