"""Pinned TavernGym 1.1.0 card-mechanism metadata audit (offline only).

Reads the engine's own card_static/card_info API, not card descriptions or
unobservable match state. The metadata is suitable for offline feature
preparation; it does NOT assert that a policy has learnt these mechanics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from .contract import (
    CATALOG_SHA256, ENGINE_HASH, PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT,
    verify_engine,
)

SESSION_ID = "s-20261102-ada5c379"
KINDS = (
    "minion", "tavern_spell", "spell", "hero", "hero_power",
    "trinket_lesser", "trinket_greater", "dark_gift", "quest", "quest_reward",
)
RACES = (
    "BEAST", "DEMON", "DRAGON", "ELEMENTAL", "MECHANICAL", "MURLOC",
    "PIRATE", "QUILBOAR", "UNDEAD", "ABERRATION", "NAGA",
)
KEYWORDS = (
    "TAUNT", "DIVINE_SHIELD", "WINDFURY", "REBORN", "VENOMOUS",
    "POISONOUS", "STEALTH", "MAGNETIC", "MEGA_WINDFURY", "CLEAVE",
    "IMMUNE", "IMMUNE_ATTACKING",
)
MECHANICS = (
    "BATTLECRY", "DEATHRATTLE", "START_OF_COMBAT", "END_OF_TURN",
    "AVENGE", "RALLY", "CHOOSE_ONE", "DISCOVER", "AURA", "MAGNETIC",
    "ACTIVATE",
)
POOLS = ("minion", "hero", "spell", "trinket")
WIDTH = 10 + 5 + 11 + 11 + 12 + 11 + 1 + 4 + 1

# These assertions are anchored to upstream *executable* Rust mechanism tests,
# not guesses from flavour text or from a live client's latest card set.
KNOWN_CASES = {
    "BGS_034": {"keywords": ("DIVINE_SHIELD", "REBORN")},
    "BG25_001": {"keywords": ("TAUNT", "REBORN")},
    "BGS_131": {"keywords": ("VENOMOUS",)},
    "BG28_300": {"mechanics": ("DEATHRATTLE",)},
}
SOURCE = {
    "card_static": "crates/taverngym-py/src/lib.rs::card_static",
    "card_definition": "crates/taverngym/src/cards.rs::CardDef",
    "keyword_mapping": "crates/taverngym/src/types.rs::Kw",
    "mechanic_mapping": "crates/taverngym/src/types.rs::Mech",
    "behavior_tests": "crates/taverngym/tests/mechanics.rs",
}


def _bits(row: np.ndarray, start: int, labels: tuple[str, ...]) -> list[str]:
    values = row[start : start + len(labels)]
    if not np.isin(values, [0.0, 1.0]).all():
        raise ValueError(f"nonbinary flags at column {start}")
    return [name for name, present in zip(labels, values) if present == 1.0]


def extract(api: object) -> dict:
    """Extract from the installed, pinned *engine*; safe to test with a fake API.

    card_static rows index by the integer card embedding index. Index 0 is
    padding, and row i exactly corresponds to card_info(i). This index must
    never be confused with the 447 observation card *slots*.
    """
    width, binary = api.card_static()
    if width != WIDTH:
        raise ValueError(f"card_static schema drift: {width} != {WIDTH}")
    count = int(api.N_CARDS)
    if count < 2:
        raise ValueError("empty card table")
    matrix = np.frombuffer(binary, dtype="<f4")
    if matrix.size != count * WIDTH:
        raise ValueError("card_static size drift")
    matrix = matrix.reshape(count, WIDTH)
    if not np.isfinite(matrix).all():
        raise ValueError("nonfinite static card features")
    if np.any(matrix[0]):
        raise ValueError("index-zero padding is nonzero")

    records = []
    seen = set()
    for idx in range(1, count):
        ident, english, chinese, tier = api.card_info(idx)
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError(f"duplicate/blank card ID at index {idx}")
        seen.add(ident)
        row = matrix[idx]
        kind = _bits(row, 0, KINDS)
        if len(kind) != 1:
            raise ValueError(f"expected one card kind: {ident}")
        if row[10] != tier:
            raise ValueError(f"tier mismatch: {ident}")
        records.append({
            "index": idx, "id": ident, "name": english, "name_zh": chinese,
            "kind": kind[0], "tier": int(tier),
            "attack": int(row[11]), "health": int(row[12]),
            "cost": int(row[13]), "armor": int(row[14]),
            "races": _bits(row, 15, RACES),
            "associated_races": _bits(row, 26, RACES),
            "keywords": _bits(row, 37, KEYWORDS),
            "mechanics": _bits(row, 49, MECHANICS),
            "golden": bool(_bits(row, 60, ("golden",))),
            "pools": _bits(row, 61, POOLS),
            "quest_goal": int(row[65]),
        })
    h = hashlib.sha256()
    h.update(bytes(binary))
    for item in records:
        h.update(item["id"].encode("utf-8"))
        h.update(b"\0")
    return {
        "schema": 1, "session_id": SESSION_ID,
        "source": SOURCE,
        "provenance": {
            "upstream_commit": UPSTREAM_COMMIT, "patch_sha256": PATCH_SHA256,
            "engine_hash": ENGINE_HASH, "ruleset_id": RULESET_ID,
            "contract_catalog_sha256": CATALOG_SHA256,
            "runtime_card_table_sha256": h.hexdigest(),
            "model_card_indices": count,
            "static_feature_width": WIDTH,
            "warning": "Metadata flags are not proof of effect execution or policy skill.",
        },
        "cards": records,
    }


def verify_known_cases(snapshot: dict) -> dict:
    index = {c["id"]: c for c in snapshot["cards"]}
    for ident, requirements in KNOWN_CASES.items():
        if ident not in index:
            raise ValueError(f"missing upstream executable-test card: {ident}")
        for field, expected in requirements.items():
            actual = index[ident][field]
            if not set(expected).issubset(actual):
                raise ValueError(f"{ident}: expected {field} {expected}, got {actual}")
    return {"source": SOURCE["behavior_tests"], "cases_passed": len(KNOWN_CASES)}


def make_summary(snapshot: dict) -> dict:
    from collections import Counter
    cards = snapshot["cards"]
    return {
        "session_id": SESSION_ID, "engine_hash": snapshot["provenance"]["engine_hash"],
        "ruleset_id": RULESET_ID, "cards": len(cards),
        "runtime_card_table_sha256": snapshot["provenance"]["runtime_card_table_sha256"],
        "kind_counts": dict(sorted(Counter(c["kind"] for c in cards).items())),
        "keyword_counts": dict(sorted(Counter(k for c in cards for k in c["keywords"]).items())),
        "mechanic_counts": dict(sorted(Counter(m for c in cards for m in c["mechanics"]).items())),
        "known_engine_test_cases": verify_known_cases(snapshot),
        "scope": "Offline static metadata only; effects and combat require separate real engine tests.",
        "training_steps": 0, "model_evaluation_games": 0,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", type=Path, required=True)
    p.add_argument("--summary", type=Path, required=True)
    args = p.parse_args()
    verify_engine()
    import taverngym
    snapshot = extract(taverngym)
    report = make_summary(snapshot)
    for target, payload in ((args.catalog, snapshot), (args.summary, report)):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
