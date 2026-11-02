"""Independent strict integrity audit for authentic TavernGym match receipts.

Does not replace the shared baseline validator. Negative mutation tests are
synthetic validation inputs and must never be represented as completed games.
"""
from __future__ import annotations

import re
from .contract import ENGINE_HASH
from .validate_receipt import validate as validate_legacy


def validate_integrity(receipt: dict) -> bool:
    """Fail closed on eight-seat integrity, provenance and policy consistency."""
    validate_legacy(receipt)
    if sorted(receipt["placements"]) != list(range(1, 9)):
        raise ValueError("Eight placements must be a permutation of 1..8")
    if type(receipt.get("seed")) is not int or receipt["seed"] < 0:
        raise ValueError("Missing or invalid integer seed")
    if receipt.get("engine_version") != "1.1.0":
        raise ValueError("Unexpected TavernGym engine version")
    if receipt.get("engine_source_hash") != ENGINE_HASH:
        raise ValueError("Unexpected pinned TavernGym source fingerprint")
    if receipt.get("policy") not in ("baseline", "model"):
        raise ValueError("Unexpected policy identifier")
    if type(receipt.get("truncated_combats")) is not int:
        raise ValueError("truncated_combats must be an integer")
    if type(receipt.get("turn_limit_end")) is not bool:
        raise ValueError("turn_limit_end must be a boolean")
    model_hash = receipt.get("model_sha256")
    if receipt["policy"] == "model":
        if not isinstance(model_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", model_hash):
            raise ValueError("Model receipts require a full SHA256 digest")
    elif model_hash is not None:
        raise ValueError("Baseline receipt must not claim a model hash")
    return True
