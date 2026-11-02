"""Source-bound TavernGym card metadata and public-action capability probes.

Engine source: MCG-NJU/AutoTavern@fb61201a557ddd36a411cf44aac51ce4d9b606ce
crates/taverngym-py/src/lib.rs (card_static/card_info/layout/action_name)
crates/taverngym/src/actions.rs and src/types.rs.
Static mechanic flags do NOT prove scripted effect behaviour or card synergy.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
from .contract import ACTIONS, CARDS, FEATURES, CATALOG_SHA256, RULESET_ID, UPSTREAM_COMMIT, verify_engine

SESSION_ID = "s-20261102-a881710a"
KINDS = ("minion", "tavern_spell", "spell", "hero", "hero_power",
         "trinket_lesser", "trinket_greater", "dark_gift", "quest", "quest_reward")
RACES = ("BEAST", "DEMON", "DRAGON", "ELEMENTAL", "MECHANICAL", "MURLOC",
         "PIRATE", "QUILBOAR", "UNDEAD", "ABERRATION", "NAGA")
KEYWORDS = ("TAUNT", "DIVINE_SHIELD", "WINDFURY", "REBORN", "VENOMOUS",
            "POISONOUS", "STEALTH", "MAGNETIC", "MEGA_WINDFURY", "CLEAVE",
            "IMMUNE", "IMMUNE_ATTACKING")
MECHANICS = ("BATTLECRY", "DEATHRATTLE", "START_OF_COMBAT", "END_OF_TURN",
             "AVENGE", "RALLY", "CHOOSE_ONE", "DISCOVER", "AURA", "MAGNETIC", "ACTIVATE")
POOLS = ("minion", "hero", "spell", "trinket")
EXPECTED_COLS = 66
ACTION_RANGES = (
    ("end_turn", 0, 1), ("refresh", 1, 2), ("freeze", 2, 3),
    ("upgrade", 3, 4), ("hero_power", 4, 6), ("dark_gift", 6, 7),
    ("cancel", 7, 8), ("buy", 8, 16), ("sell", 16, 23),
    ("activate", 23, 30), ("choose", 30, 46), ("play", 46, 126),
    ("magnetize", 126, 196), ("move", 196, 245),
)


def decode_row(index: int, info: tuple, row: np.ndarray) -> dict:
    """Only compiler-encoded facts, never inferred effects."""
    if row.shape != (EXPECTED_COLS,) or not np.isfinite(row).all():
        raise ValueError("card_static row shape/nonfinite data")
    flag_indices = list(range(10)) + list(range(15, 65))
    if not np.isin(row[flag_indices], [0.0, 1.0]).all():
        raise ValueError("card_static flag is not binary")
    if int(np.sum(row[:10])) != 1:
        raise ValueError("card kind is not one-hot")
    card_id, name_en, name_zh, tier = info
    if int(row[10]) != int(tier):
        raise ValueError("card_info tier disagrees with card_static")
    flags = lambda xs, lo: [name for j, name in enumerate(xs) if row[lo+j] == 1.0]
    return {
        "embedding_index": index, "card_id": card_id,
        "name_en": name_en, "name_zh": name_zh, "kind": KINDS[int(np.argmax(row[:10]))],
        "tier": int(tier), "attack": int(row[11]), "health": int(row[12]),
        "cost": int(row[13]), "armor": int(row[14]),
        "races": flags(RACES, 15), "hero_associated_races": flags(RACES, 26),
        "keywords": flags(KEYWORDS, 37), "printed_mechanics": flags(MECHANICS, 49),
        "golden": bool(row[60]),
        "static_pool_flags": flags(POOLS, 61), "quest_goal": int(row[65]),
        "effect_script_verified": False,
    }


def action_family(action: int) -> str:
    if not 0 <= action < ACTIONS:
        raise ValueError("action index outside pinned 245-action space")
    return next(label for label, lo, hi in ACTION_RANGES if lo <= action < hi)


def extract_catalog() -> tuple[dict, dict]:
    import taverngym
    engine = verify_engine()
    layout = dict(taverngym.layout())
    required = {"A_HERO_POWER": 4, "A_DARK_GIFT": 6, "A_CANCEL": 7, "A_BUY": 8,
                "A_SELL": 16, "A_ACTIVATE": 23, "A_CHOOSE": 30, "A_PLAY": 46,
                "A_MAGNETIZE": 126, "A_MOVE": 196, "N_ACTIONS": ACTIONS}
    for k, expected in required.items():
        if layout.get(k) != expected:
            raise ValueError(f"action-layout drift {k}: {layout.get(k)} != {expected}")
    if sum(hi - lo for _, lo, hi in ACTION_RANGES) != ACTIONS:
        raise ValueError("action families incomplete")
    names = {str(a): taverngym.action_name(a) for a in range(ACTIONS)}
    if len(set(names.values())) != ACTIONS:
        raise ValueError("action names are not unique")
    width, raw = taverngym.card_static()
    if int(width) != EXPECTED_COLS:
        raise ValueError(f"card_static width drift: {width}")
    rows = np.frombuffer(raw, dtype="<f4")
    if rows.size % EXPECTED_COLS:
        raise ValueError("invalid card_static byte length")
    rows = rows.reshape(-1, EXPECTED_COLS)
    if len(rows) != int(taverngym.N_CARDS) or not np.all(rows[0] == 0):
        raise ValueError("card_static embedding index layout drift")
    cards = [decode_row(i, taverngym.card_info(i), rows[i])
             for i in range(1, len(rows))]
    if len({c["card_id"] for c in cards}) != len(cards):
        raise ValueError("duplicate card identifiers")
    catalog = {
        "schema": 1, "session_id": SESSION_ID, "engine": engine,
        "upstream_commit": UPSTREAM_COMMIT, "ruleset_id": RULESET_ID,
        "pinned_catalog_sha256": CATALOG_SHA256,
        "source": "crates/taverngym-py/src/lib.rs::card_static; crates/taverngym/src/types.rs",
        "limitations": "Static metadata only; trigger effects and synergies unverified; pool flags are not lobby availability.",
        "cards": cards,
        "actions": names, "action_ranges": [
            {"family": label, "start": lo, "stop_exclusive": hi}
            for label, lo, hi in ACTION_RANGES
        ],
        "layout": layout,
    }
    counts = {
        "card_kinds": dict(Counter(c["kind"] for c in cards)),
        "printed_mechanics": dict(Counter(m for c in cards for m in c["printed_mechanics"])),
        "keywords": dict(Counter(k for c in cards for k in c["keywords"])),
    }
    summary = {
        "schema": 1, "session_id": SESSION_ID, "engine": engine,
        "upstream_commit": UPSTREAM_COMMIT, "cards": len(cards),
        "actions": ACTIONS, "static_width": EXPECTED_COLS, "counts": counts,
        "mechanics_not_verified": True,
    }
    return catalog, summary


def probe_game(seed: int) -> dict:
    """Observe only public observation/mask for our seat; bots control other 7."""
    import taverngym
    from .baseline import BaselinePolicy
    verify_engine()
    game, bot = taverngym.Game(seed=seed), BaselinePolicy()
    last_turn, used, n_decisions, selected, legal_counts = -1, 0, 0, Counter(), Counter()
    for _ in range(30000):
        if game.is_over():
            break
        turn = int(game.turn)
        if turn != last_turn:
            last_turn, used = turn, 0
        progressed = False
        for seat in range(game.num_players):
            if not game.needs_action(seat):
                continue
            progressed = True
            if seat:
                game.bot_play(seat)
                continue
            fbytes, cbytes = game.observe2(0)
            features = np.frombuffer(fbytes, dtype="<f4")
            cards = np.frombuffer(cbytes, dtype="<i4")
            mask = np.frombuffer(game.legal_mask(0), dtype=np.uint8).astype(bool)
            if features.shape != (FEATURES,) or cards.shape != (CARDS,) or mask.shape != (ACTIONS,):
                raise ValueError("public observation shape drift")
            if not np.isfinite(features).all() or np.any(cards < 0) or np.any(cards >= taverngym.N_CARDS):
                raise ValueError("invalid public observation/card index")
            if not mask.any():
                raise ValueError("no legal actions while action required")
            for a in np.flatnonzero(mask):
                legal_counts[action_family(int(a))] += 1
            action = bot.act({"features": features, "cards": cards, "action_mask": mask},
                             {"turn": turn, "actions_used": used})
            if not mask[action]:
                raise ValueError("baseline selected illegal action")
            selected[action_family(action)] += 1
            game.step(0, action)
            used += 1
            n_decisions += 1
        if not progressed and not game.is_over():
            raise RuntimeError("full game stalled")
    if not game.is_over():
        raise RuntimeError("full game safety bound exceeded")
    return {
        "seed": seed, "completed": True, "turns": int(game.turn),
        "decisions": n_decisions, "seat0_placement": int(game.placements()[0]),
        "truncated_combats": int(game.truncated_combats),
        "turn_limit_end": bool(game.turn_limit_end),
        "selected_families": dict(selected), "legal_family_occurrences": dict(legal_counts),
        "policy": "unchanged_baseline_instrumented_not_strength_candidate",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=27861)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    catalog, summary = extract_catalog()
    a.out.mkdir(parents=True, exist_ok=True)
    full_text = json.dumps(catalog, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    (a.out / "catalog-full.json").write_text(full_text + "\n", encoding="utf-8")
    summary["catalog_output_sha256"] = hashlib.sha256((full_text + "\n").encode("utf-8")).hexdigest()
    result = probe_game(a.seed)
    (a.out / "catalog-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (a.out / "probe-summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("CATALOG_SUMMARY " + json.dumps(summary, ensure_ascii=False))
    print("ENGINE_PROBE " + json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
