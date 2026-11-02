"""Pure, offline regression gates; no model-performance claims."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from tavern_ai.registry_integrity import validate_registry, verify_checkpoint


ROOT = Path(__file__).resolve().parents[1]


def registry():
    return json.loads((ROOT / "models" / "registry.json").read_text("utf-8"))


def test_source_registry_is_consistent_and_unpromoted():
    result = validate_registry(registry())
    assert result["latest_id"] == "v2-learning-41413557445"
    assert result["latest_steps"] == 1280
    assert result["champion"] is None
    assert result["checkpoint_bytes_checked"] is False


@pytest.mark.parametrize("mutation", ["champion", "sha", "engine", "latest", "duplicate", "url"])
def test_reject_incompatible_or_unproven_manifest(mutation):
    item = copy.deepcopy(registry())
    if mutation == "champion":
        item["best"] = item["latest"]["id"]
    elif mutation == "sha":
        item["candidates"][0]["checkpoint_sha256"] = "0" * 63
    elif mutation == "engine":
        item["engine"]["card_slots"] = 446
    elif mutation == "latest":
        item["latest"]["training_steps"] = -1
    elif mutation == "duplicate":
        item["candidates"].append(copy.deepcopy(item["candidates"][0]))
    else:
        item["candidates"][0]["release_url"] = "https://example.invalid/model.zip"
    with pytest.raises(ValueError):
        validate_registry(item)


def test_checkpoint_hash_verification_refuses_corruption(tmp_path):
    path = tmp_path / "model.zip"
    path.write_bytes(b"test-only-fake-not-a-real-model")
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    assert verify_checkpoint(path, expected) == expected
    path.write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="mismatch"):
        verify_checkpoint(path, expected)
