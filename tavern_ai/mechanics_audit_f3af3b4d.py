"""Pinned-engine mechanics audit; offline oracle is NEVER a deployed policy input.

This module does not train weights, infer card effects from text, or use hidden
opponent/RNG state as an action feature. The debug API is used only in isolated
engine-mechanics probes, never in a competitive policy or benchmark.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from .contract import (
    ACTIONS, CARDS, CATALOG_SHA256, ENGINE_HASH, FEATURES,
    PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT, verify_engine,
)

ACTION_FAMILIES = (
    (0, 1, "end"), (1, 2, "refresh"), (2, 3, "freeze"),
    (3, 4, "upgrade"), (4, 6, "hero_power"),
    (6, 7, "dark_gift"), (7, 8, "cancel"),
    (8, 16, "buy"), (16, 23, "sell"), (23, 30, "activate"),
    (30, 46, "choose"), (46, 126, "play"),
    (126, 196, "magnetize"), (196, 245, "move"),
)

def action_family(index: int) -> str:
    if not 0 <= index < ACTIONS:
        raise ValueError("out of bounds action index")
    return next(name for start, end, name in ACTION_FAMILIES
                if start <= index < end)

def check_action_names(tg) -> dict:
    prefixes = {
        "end": "EndTurn", "refresh": "Refresh", "freeze": "Freeze",
        "upgrade": "Upgrade", "hero_power": "HeroPower",
        "dark_gift": "DarkGift", "cancel": "Cancel",
        "buy": "Buy", "sell": "Sell", "activate": "Activate",
        "choose": "Choose", "play": "Play",
        "magnetize": "Magnetize", "move": "Move",
    }
    counts = Counter()
    for index in range(ACTIONS):
        family = action_family(index)
        actual = tg.action_name(index)
        if not actual.startswith(prefixes[family]):
            raise AssertionError(f"index {index}: {actual!r} != {family}")
        counts[family] += 1
    try:
        tg.action_name(ACTIONS)
    except ValueError:
        pass
    else:
        raise AssertionError("out-of-range action did not fail")
    return dict(sorted(counts.items()))

def normalize_catalog(raw: list[dict]) -> list[dict]:
    if not isinstance(raw, list) or not raw:
        raise ValueError("empty or malformed engine card catalog")
    wanted = (
        "cid", "id", "name", "name_zh", "kind", "tier", "atk", "hp",
        "cost", "races", "implemented", "scripted", "reachable",
        "in_pool", "golden_id", "normal_id", "hero_power_id", "tier7",
    )
    out, ids = [], set()
    for n, card in enumerate(raw):
        if not isinstance(card, dict) or card.get("cid") != n:
            raise ValueError(f"card table reordered at index {n}")
        if not all(key in card for key in wanted):
            raise ValueError(f"missing engine catalog key at {n}")
        if not isinstance(card["id"], str) or card["id"] in ids:
            raise ValueError(f"invalid or duplicate card id at {n}")
        ids.add(card["id"])
        out.append({key: card[key] for key in wanted})
    return out

def audit_catalog(tg) -> tuple[list[dict], dict]:
    cards = normalize_catalog(json.loads(tg.catalog_json()))
    if len(cards) + 1 != tg.N_CARDS:
        raise AssertionError("engine catalog count disagrees with embedding table")
    for card in cards:
        cid = int(card["cid"])
        id_, name, name_zh, tier = tg.card_info(cid + 1)
        if (id_, name, name_zh, tier) != (
            card["id"], card["name"], card["name_zh"], card["tier"]
        ):
            raise AssertionError(f"card_info index mismatch at cid {cid}")
    text = json.dumps(cards, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    coverage = {
        "all_cards": len(cards),
        "embedding_vocab_including_padding": tg.N_CARDS,
        "in_pool": sum(bool(c["in_pool"]) for c in cards),
        "reachable": sum(bool(c["reachable"]) for c in cards),
        "scripted": sum(bool(c["scripted"]) for c in cards),
        "implemented": sum(bool(c["implemented"]) for c in cards),
        "reachable_pool_implemented": sum(
            bool(c["reachable"]) and bool(c["in_pool"]) and bool(c["implemented"])
            for c in cards
        ),
        "types": dict(sorted(Counter(c["kind"] for c in cards).items())),
        "generated_catalog_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "limits": "Engine metadata flags are not effect-trigger verification.",
    }
    return cards, coverage

def _mask(game, player=0) -> list[bool]:
    raw = list(game.legal_mask(player))
    if len(raw) != ACTIONS or any(v not in (0, 1, False, True) for v in raw):
        raise AssertionError("invalid engine mask")
    return [bool(v) for v in raw]

def probe_economy(tg, seed: int) -> dict:
    """Source-backed true engine instances with gold changed by its debug API.

    These are CONTROLLED MECHANICS TESTS, not natural policy rollouts.
    The debug view is an oracle; only the own-seat 'me' block is read.
    """
    game = tg.Game(seed=seed)
    initial = _mask(game)
    choices = [n for n in range(30, 46) if initial[n]]
    if not choices:
        raise AssertionError("expected actual initial hero-selection mask")
    if any(initial[n] for n in range(ACTIONS) if n not in (*range(30, 46), 7)):
        raise AssertionError("pending hero choice exposed non-choice action")
    for seat in range(game.num_players):
        allowed = _mask(game, seat)
        picks = [n for n in range(30, 46) if allowed[n]]
        if not picks:
            raise AssertionError(f"hero selection missing at seat {seat}")
        game.step(seat, picks[0])

    def own(g):
        return json.loads(g.view(0))["me"]

    def change_gold(g, amount):
        g.debug(json.dumps({"cmd": "set_player", "p": 0, "gold": amount}))
        if own(g)["gold"] != amount:
            raise AssertionError("debug gold intervention failed")

    low, high = game.copy(), game.copy()
    change_gold(low, 0)
    change_gold(high, 100)
    m0, m100 = _mask(low), _mask(high)
    a0, a100 = own(low), own(high)
    if any(m0[n] and not m100[n] for n in [1, 3, *range(8, 16)]):
        raise AssertionError("legal paid actions shrank when gold increased")
    tested_costs = 0
    for i, slot in enumerate(a0["shop"][:8]):
        cost = slot.get("price")
        if isinstance(cost, (int, float)) and cost > 0 and not slot.get("costs_health"):
            if m0[8+i]:
                raise AssertionError(f"unaffordable slot {i} legally purchasable")
            tested_costs += 1

    transitions = {}
    if m100[2]:
        clone = high.copy()
        before, gold_before = own(clone)["frozen"], own(clone)["gold"]
        clone.step(0, 2)
        transitions["freeze"] = {
            "executed": True, "toggled": before != own(clone)["frozen"],
            "gold_delta": own(clone)["gold"] - gold_before,
        }
        if not transitions["freeze"]["toggled"]:
            raise AssertionError("Freeze did not flip frozen flag")
    if m100[3]:
        clone = high.copy()
        tier_before = own(clone)["tier"]
        clone.step(0, 3)
        tier_after = own(clone)["tier"]
        transitions["upgrade"] = {"executed": True, "tier_before": tier_before,
                                  "tier_after": tier_after}
        if tier_after != tier_before + 1:
            raise AssertionError("Upgrade did not increase tavern tier by exactly one")
    buys = [a for a in range(8, 16) if m100[a]]
    if buys:
        clone = high.copy()
        before = own(clone)
        clone.step(0, buys[0])
        after = own(clone)
        transitions["buy"] = {
            "executed": True, "index": buys[0],
            "gold_before": before["gold"], "gold_after": after["gold"],
            "hand_before": len(before["hand"]), "hand_after": len(after["hand"]),
        }
    if m100[1]:
        clone = high.copy()
        clone.step(0, 1)
        transitions["refresh"] = {"executed": True, "shop_after": len(own(clone)["shop"])}
    if m100[0]:
        clone = high.copy()
        clone.step(0, 0)
        transitions["end"] = {
            "executed": True, "still_needs_action": clone.needs_action(0)
        }
        if transitions["end"]["still_needs_action"]:
            raise AssertionError("EndTurn left same seat requiring action")
    return {
        "seed": seed, "initial_choice_count": len(choices),
        "zero_gold_legal_buy_count": sum(m0[8:16]),
        "high_gold_legal_buy_count": sum(m100[8:16]),
        "positive_price_unaffordable_cases": tested_costs,
        "transitions": transitions,
        "warning": "Debug gold interventions are not natural game observations or training inputs.",
    }

def run(out_dir: Path, agent_id: str, seed: int) -> dict:
    import taverngym as tg
    from .canary import run as full_match
    engine = verify_engine()
    action_counts = check_action_names(tg)
    cards, card_coverage = audit_catalog(tg)
    probes = [probe_economy(tg, seed), probe_economy(tg, seed + 1)]
    out_dir.mkdir(parents=True, exist_ok=True)
    compact = {
        "schema": 1, "source": "runtime taverngym.catalog_json",
        "upstream_commit": UPSTREAM_COMMIT, "patch_sha256": PATCH_SHA256,
        "engine_source_hash": ENGINE_HASH, "ruleset_id": RULESET_ID,
        "pinned_card_data_sha256": CATALOG_SHA256,
        "encoding": "cid is zero-based; observe2 card index is cid+1; zero is padding",
        "status": "static metadata only; printed text does not prove trigger logic",
        "cards": cards,
    }
    (out_dir / "001-engine-card-catalog.json").write_text(
        json.dumps(compact, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    receipt = full_match(seed + 2, agent_id=agent_id, policy="baseline")
    (out_dir / "001-real-eight-seat.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    summary = {
        "schema": 1, "agent_id": agent_id, "engine": engine,
        "seed": seed, "action_partitions": action_counts,
        "card_coverage": card_coverage, "controlled_mechanics_probes": probes,
        "full_match_receipt": "001-real-eight-seat.json",
        "full_match_rank": receipt["placements"][0],
        "train_steps": 0, "model_checkpoint": None, "strength_claim": None,
        "features": FEATURES, "card_slots": CARDS, "actions": ACTIONS,
        "limits": [
            "No PPO/BC training and no learned strategy demonstrated.",
            "Catalog effect flags do not verify the meaning of card text.",
            "Debug interventions never enter policy observations.",
            "One baseline full-match is an engineering gate, not evidence of improvement.",
        ],
    }
    (out_dir / "001-mechanics-results.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--agent-id", required=True)
    p.add_argument("--seed", type=int, default=78101)
    args = p.parse_args()
    print(json.dumps(run(args.out_dir, args.agent_id, args.seed), ensure_ascii=False))

if __name__ == "__main__":
    main()
