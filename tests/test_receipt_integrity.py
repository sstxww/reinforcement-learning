import copy
import pytest

from tavern_ai.contract import ENGINE_HASH
from tavern_ai.receipt_integrity import validate_integrity
from tavern_ai.validate_receipt import validate as legacy_validate
from tavern_ai.receipt_audit_experiment import mutations


def authentic_shape():
    return {
        "environment": "TavernGym", "completed": True, "agent_id": "test",
        "placements": [1, 2, 3, 4, 5, 6, 7, 8],
        "turns": 12, "decisions": 42, "truncated_combats": 0,
        "turn_limit_end": False, "seed": 36001, "policy": "baseline",
        "engine_version": "1.1.0", "engine_source_hash": ENGINE_HASH,
        "model_sha256": None
    }


def test_authentic_shape_passes():
    assert validate_integrity(authentic_shape())


def test_base_and_strict_reject_duplicate_ranks():
    false_receipt = copy.deepcopy(authentic_shape())
    false_receipt["placements"] = [1, 1, 3, 4, 5, 6, 7, 8]
    with pytest.raises(ValueError, match="permutation"):
        legacy_validate(false_receipt)
    with pytest.raises(ValueError, match="permutation"):
        validate_integrity(false_receipt)


@pytest.mark.parametrize("mutator", [
    lambda r: r.update(seed=True),
    lambda r: r.update(seed=-1),
    lambda r: r.update(engine_source_hash="wrong"),
    lambda r: r.update(engine_version="0.0"),
    lambda r: r.update(policy="model"),
    lambda r: r.update(model_sha256="f" * 64),
    lambda r: r.update(turn_limit_end=0),
    lambda r: r.update(truncated_combats=False),
])
def test_strict_invalid_mutations(mutator):
    r = authentic_shape()
    mutator(r)
    with pytest.raises(ValueError):
        validate_integrity(r)


def test_model_hash_valid():
    r = authentic_shape()
    r["policy"] = "model"
    r["model_sha256"] = "a" * 64
    assert validate_integrity(r)


def test_all_synthetic_mutations_rejected():
    for name, fake in mutations(authentic_shape()).items():
        with pytest.raises(ValueError), pytest.MonkeyPatch.context() as _:
            validate_integrity(fake)
