"""V5 bounded, no-fallback model behavior and checkpoint archive audit.

All counters use only the public observe2 policy input, legal mask, and
controlled-seat action. This does not infer gold or card abilities.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from .contract import ACTIONS, CARDS, FEATURES, verify_engine


def action_family(action: int) -> str:
    if action == 0:
        return "end_turn"
    if action == 1:
        return "refresh"
    if action == 3:
        return "upgrade"
    if 8 <= action <= 15:
        return "buy"
    if 16 <= action <= 22:
        return "sell"
    if 30 <= action <= 45:
        return "choose"
    if 46 <= action <= 125:
        return "play"
    return "other"


def archive_gate(model_path: Path, metadata_path: Path, expected_sha256: str) -> dict:
    """Check file identity, archive CRC, optimizer state and engine metadata."""
    if len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise ValueError("A full lowercase SHA256 must be pinned")
    if not model_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("Both weights and metadata must exist")
    digest = hashlib.file_digest(model_path.open("rb"), "sha256").hexdigest()
    if digest != expected_sha256:
        raise ValueError("Checkpoint SHA256 mismatch")
    with zipfile.ZipFile(model_path) as archive:
        contents = set(archive.namelist())
        if not {"data", "policy.pth", "policy.optimizer.pth"}.issubset(contents):
            raise ValueError("Checkpoint is missing model/optimizer state")
        if archive.testzip() is not None:
            raise ValueError("Checkpoint ZIP CRC mismatch")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    engine = verify_engine()
    if metadata.get("engine") != engine:
        raise ValueError("Checkpoint engine/card-vocabulary incompatible")
    steps = metadata.get("total_timesteps")
    if type(steps) is not int or steps < 1:
        raise ValueError("Checkpoint has no trustworthy training step count")
    return {"model_sha256": digest, "metadata_steps": steps, "engine": engine,
            "optimizer_present": True, "zip_crc_ok": True}


def audit_game(model_path: Path, seed: int, max_decisions: int) -> dict:
    """Run real eight-seat gameplay, recording model-only public action evidence.

    An interrupted game is explicitly incomplete: NEVER a successful receipt.
    """
    if seed < 0 or not 1 <= max_decisions <= 5000:
        raise ValueError("Require nonnegative seed and 1..5000 model decisions")
    import numpy as np
    import taverngym
    from sb3_contrib import MaskablePPO

    model = MaskablePPO.load(str(model_path), device="cpu")
    game = taverngym.Game(seed=seed)
    if game.num_players != 8:
        raise RuntimeError("Expected real eight-seat TavernGym")
    counts = Counter()
    opportunities = Counter()
    by_turn = defaultdict(Counter)
    last = None
    repeats = 0
    decisions = 0
    completed = False
    for _ in range(30000):
        if game.is_over():
            completed = True
            break
        advanced = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            advanced = True
            if seat:
                game.bot_play(seat)
                continue
            if decisions >= max_decisions:
                break
            fb, cb = game.observe2(0)
            raw_mask = game.legal_mask(0)
            f = np.frombuffer(fb, dtype="<f4").copy()
            c = np.frombuffer(cb, dtype="<i4").copy()
            mask = np.frombuffer(raw_mask, dtype=np.uint8).astype(bool)
            if f.shape != (FEATURES,) or c.shape != (CARDS,) or mask.shape != (ACTIONS,) or not mask.any():
                raise ValueError("Unexpected observe2/legality contract")
            act, _ = model.predict({"features": f, "cards": c},
                                   action_masks=mask, deterministic=True)
            action = int(act)
            if action < 0 or action >= ACTIONS or not mask[action]:
                raise ValueError("Model emitted an illegal action")
            turn = int(game.turn)
            buy_legal = bool(mask[8:16].any())
            if buy_legal:
                opportunities["buy_legal_decisions"] += 1
            if buy_legal and action == 0:
                opportunities["end_with_buy_legal"] += 1
            if buy_legal and 8 <= action <= 15:
                opportunities["buy_selected_when_legal"] += 1
            fingerprint = hashlib.sha256(fb + cb + raw_mask).hexdigest()[:16]
            if last == (turn, action, fingerprint):
                repeats += 1
            last = (turn, action, fingerprint)
            family = action_family(action)
            counts[family] += 1
            by_turn[str(turn)][family] += 1
            game.step(0, action)
            decisions += 1
        if decisions >= max_decisions:
            completed = bool(game.is_over())
            break
        if not advanced and not game.is_over():
            raise RuntimeError("Game stalled")
    if game.is_over():
        completed = True
    return {
        "schema": 1, "policy": "model_without_fallback", "seed": seed,
        "completed": completed, "incomplete_reason": None if completed else "decision_budget_or_iteration_limit",
        "decisions": decisions, "turns_reached": int(game.turn),
        "agent_placement": int(game.placements()[0]) if completed else None,
        "placements": [int(x) for x in game.placements()] if completed else None,
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "action_counts": dict(counts), "legal_opportunities": dict(opportunities),
        "same_observation_action_repeat_count": repeats,
        "per_turn_action_counts": {k: dict(v) for k, v in sorted(by_turn.items(), key=lambda e: int(e[0]))},
        "forced_end_turns": 0, "baseline_fallback_actions": 0,
        "warning": "Legal BUY availability is not proof that buying was affordable or strategically good.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--seed", type=int, default=945077)
    p.add_argument("--max-decisions", type=int, default=800)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    audit = archive_gate(a.model, a.metadata, a.expected_sha256)
    report = {"checkpoint": audit, "game": audit_game(a.model, a.seed, a.max_decisions),
              "training_steps_this_audit": 0,
              "champion_promotion": False,
              "not_a_receipt_if_incomplete": True}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"sha256": audit["model_sha256"], "game": report["game"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
