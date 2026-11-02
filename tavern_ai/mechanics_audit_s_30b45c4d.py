"""Pinned TavernGym public-mechanics audit; evidence, NOT an improved policy.

Source: MCG-NJU/AutoTavern@fb61201a557ddd36a411cf44aac51ce4d9b606ce
         crates/taverngym/data/cards.json and src/actions.rs.
The card catalog may contain unpooled cards; card text/keywords are NOT proof
of implemented combat triggers. All observations used here come from observe2.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .baseline import BaselinePolicy
from .contract import ACTIONS, CARDS, FEATURES, UPSTREAM_COMMIT, verify_engine
from .validate_receipt import validate

SESSION_ID = "s-20261102-30b45c4d"
SOURCE = "crates/taverngym/data/cards.json"
ACTION_SOURCE = "crates/taverngym/src/actions.rs"
# Exact half-open ranges from the pinned upstream Rust Action::{encode,decode}.
ACTION_FAMILIES = (
    ("end_turn", 0, 1),
    ("refresh", 1, 2),
    ("freeze", 2, 3),
    ("upgrade", 3, 4),
    ("hero_power", 4, 6),
    ("dark_gift", 6, 7),
    ("cancel", 7, 8),
    ("buy", 8, 16),
    ("sell", 16, 23),
    ("activate", 23, 30),
    ("choose", 30, 46),
    ("play", 46, 126),
    ("magnetize", 126, 196),
    ("move", 196, 245),
)


def action_family(action: int) -> str:
    if not isinstance(action, (int, np.integer)) or not 0 <= action < ACTIONS:
        raise ValueError(f"Action out of bounds: {action!r}")
    return next(name for name, lo, hi in ACTION_FAMILIES if lo <= action < hi)


def decode_action(action: int) -> dict:
    """Parameters are derived from Rust layout, not the action-mask heuristics."""
    name = action_family(action)
    if name == "play":
        k = action - 46
        return {"family": name, "hand": k // 8, "position": k % 8}
    if name == "magnetize":
        k = action - 126
        return {"family": name, "hand": k // 7, "board": k % 7}
    if name == "move":
        k = action - 196
        return {"family": name, "from": k // 7, "to": k % 7}
    if name in {"buy", "sell", "activate", "choose", "hero_power"}:
        starts = {"buy": 8, "sell": 16, "activate": 23,
                  "choose": 30, "hero_power": 4}
        return {"family": name, "slot": action - starts[name]}
    return {"family": name}


def build_catalog(source_path: Path) -> tuple[list[dict], dict]:
    """Preserve physical card indices and explicit pool membership.

    No text-derived claims about script implementation or strategic synergy.
    This must be built from the exact upstream source in the pinned checkout.
    """
    raw_bytes = source_path.read_bytes()
    raw = json.loads(raw_bytes)
    cards = raw["cards"]
    meta = raw["meta"]
    if not isinstance(cards, list) or not cards or not isinstance(meta, dict):
        raise ValueError("Invalid upstream card catalog")
    if meta.get("server_patch") != "36.6.3":
        raise ValueError("Unexpected ruleset version")
    ids = [c["id"] for c in cards]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate upstream card IDs")
    for key in ("kind", "tier", "races", "keywords", "pools", "text"):
        if any(key not in c for c in cards):
            raise ValueError(f"Missing catalog field: {key}")
    # observe2 card ID 0 is padding; engine encodes CardId(i) as i+1.
    index = [
        {
            "observation_card_index": i + 1, "card_id": c["id"],
            "name": c.get("name", ""), "name_zh": c.get("name_zh", ""),
            "kind": c["kind"], "tier": c["tier"],
            "attack": c.get("atk", 0), "health": c.get("hp", 0),
            "races": c["races"], "keywords": c["keywords"],
            "pools": c["pools"], "golden_id": c.get("golden", ""),
            "normal_id": c.get("normal", ""),
            "effect_text": c["text"],
            "effect_verification": "NOT_VERIFIED_BY_TEXT",
        }
        for i, c in enumerate(cards)
    ]
    kinds = Counter(c["kind"] for c in cards)
    pools = Counter(pool for c in cards for pool in c["pools"])
    keywords = Counter(kw for c in cards for kw in c["keywords"])
    summary = {
        "session_id": SESSION_ID, "source_commit": UPSTREAM_COMMIT,
        "source_path": SOURCE,
        "action_source_path": ACTION_SOURCE,
        "source_file_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "client_version": meta.get("client_version"),
        "server_patch": meta.get("server_patch"),
        "card_count": len(cards),
        "unique_card_ids": len(ids),
        "pool_counts": dict(sorted(pools.items())),
        "kind_counts": dict(sorted(kinds.items())),
        "keyword_counts": dict(sorted(keywords.items())),
        "cards_with_text": sum(bool(c["text"]) for c in cards),
        "cards_without_pools": sum(not c["pools"] for c in cards),
        "action_family_lengths": {name: hi - lo for name, lo, hi in ACTION_FAMILIES},
        "interpretation": (
            "Catalog entries are not necessarily in current game pools. "
            "Keywords/text are labels, not evidence that effects execute."
        ),
    }
    return index, summary


def audit_full_game(seed: int) -> tuple[dict, dict]:
    """A real finished eight-seat game; original baseline, not a learned model."""
    import taverngym

    engine = verify_engine()
    game = taverngym.Game(seed=seed)
    baseline = BaselinePolicy()
    decisions = 0
    illegal = 0
    choices = 0
    last_turn = -1
    turn_decisions = 0
    actual_actions = Counter()
    available_families = Counter()
    per_turn = defaultdict(int)
    repeated_public_observation = 0
    seen_public = set()

    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, turn_decisions = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat != 0:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            f = np.frombuffer(fbytes, dtype="<f4").copy()
            c = np.frombuffer(cbytes, dtype="<i4").copy()
            mask_bytes = game.legal_mask(0)
            mask = np.frombuffer(mask_bytes, dtype=np.uint8).astype(bool)
            if (f.shape, c.shape, mask.shape) != (
                (FEATURES,), (CARDS,), (ACTIONS,)
            ):
                raise ValueError("Observation contract mismatch")
            if not np.isfinite(f).all() or not mask.any():
                raise ValueError("Invalid public state or empty legal mask")
            legal = np.flatnonzero(mask)
            families = {action_family(int(a)) for a in legal}
            for family in families:
                available_families[family] += 1
            if "choose" in families:
                choices += 1
                if any(a not in range(30, 46) and a != 7 for a in legal):
                    raise AssertionError("Pending choice exposed unrelated actions")
            public_hash = hashlib.sha256(
                fbytes + cbytes + bytes(mask_bytes)
            ).hexdigest()
            if public_hash in seen_public:
                repeated_public_observation += 1
            seen_public.add(public_hash)
            action = int(baseline.act(
                {"features": f, "cards": c, "action_mask": mask},
                {"turn": turn, "actions_used": turn_decisions},
            ))
            if not mask[action]:
                illegal += 1
                raise AssertionError("Baseline selected an illegal action")
            game.step(0, action)
            actual_actions[action_family(action)] += 1
            decisions += 1
            turn_decisions += 1
            per_turn[str(turn)] += 1
        if not progressed and not game.is_over():
            raise RuntimeError("Real game stalled")
    if not game.is_over():
        raise RuntimeError("Real game exceeded finite safety bound")
    placements = [int(x) for x in game.placements()]
    receipt = {
        "schema": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "TavernGym", "engine_version": engine["version"],
        "engine_source_hash": engine["source_hash"],
        "agent_id": SESSION_ID, "policy": "baseline",
        "seed": seed, "completed": True, "turns": int(game.turn),
        "decisions": decisions, "placements": placements,
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "model_sha256": None,
        "study": "public_mechanics_only_not_policy_improvement",
    }
    validate(receipt)
    audit = {
        "seed": seed, "observation_dimensions": [FEATURES, CARDS, ACTIONS],
        "model_training_steps": 0, "candidate_policy": "original_baseline",
        "total_decisions": decisions, "illegal_actions": illegal,
        "choice_pending_observations": choices,
        "available_family_observations": dict(sorted(available_families.items())),
        "actual_action_families": dict(sorted(actual_actions.items())),
        "actions_per_turn": dict(sorted(per_turn.items(), key=lambda x: int(x[0]))),
        "repeated_public_observation_hashes": repeated_public_observation,
        "observation_source": "observe2 + legal_mask(seat=0) only",
        "result": {"placement_seat0": placements[0], "complete": True},
    }
    return receipt, audit


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--seed", type=int, default=83171)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    index, summary = build_catalog(args.source)
    engine = verify_engine()
    if len(index) + 1 != engine["n_cards"]:
        raise RuntimeError("Catalog size + zero-padding differs from live engine card vocabulary")
    receipt, audit = audit_full_game(args.seed)
    summary["live_engine"] = engine
    summary["full_game_audit"] = audit
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in (
        ("card-index.json", index),
        ("summary.json", summary),
        ("receipt.json", receipt),
    ):
        (args.output_dir / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(json.dumps({
        "session_id": SESSION_ID, "card_count": len(index),
        "source_file_sha256": summary["source_file_sha256"],
        "pool_counts": summary["pool_counts"],
        "action_families": summary["action_family_lengths"],
        "game_audit": audit,
        "receipt": receipt,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
