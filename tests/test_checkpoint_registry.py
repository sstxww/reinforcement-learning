"""Pure-Python verification tests; synthetic bytes are NEVER real trained models."""
import copy
import hashlib
import json
from pathlib import Path
import pytest
from tavern_ai.checkpoint_registry import validate_registry, verify_local
from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

def good(tmp_path):
    weights = tmp_path / "model.zip"
    weights.write_bytes(b"synthetic bytes ONLY, not a trained model")
    metadata = tmp_path / "model.metadata.json"
    metadata.write_text(json.dumps({"engine": {"version": "1.1.0",
        "source_hash": ENGINE_HASH, "features": FEATURES, "cards": CARDS,
        "actions": ACTIONS}, "total_timesteps": 256}))
    model_id = "test-release"
    base = f"https://github.com/sstxww/reinforcement-learning/releases/download/{model_id}/"
    entry = {"id": model_id, "role": "Population", "train_steps": 256, "parent_id": None,
        "weights": {"url": base + "model.zip",
                    "sha256": hashlib.sha256(weights.read_bytes()).hexdigest()},
        "metadata": {"url": base + "model.metadata.json",
                     "sha256": hashlib.sha256(metadata.read_bytes()).hexdigest()},
        "verification": {"release_indexed": True, "weights_download_hash_checked": False,
          "metadata_download_hash_checked": False, "sb3_load_checked": False,
          "training_resume_checked": False, "full_game_checked": False}}
    return {"schema": 1, "champion_id": None,
            "latest_resumable_id": None, "models": [entry]}, weights, metadata

def test_good_hash_and_engine(tmp_path):
    registry, weights, metadata = good(tmp_path)
    result = verify_local(registry, "test-release", weights, metadata)
    assert result["weights_sha256_ok"] and result["metadata_sha256_ok"]
    assert result["sb3_load_checked"] is False
    assert result["training_resume_checked"] is False

def test_tampered_weights_fail_before_model_load(tmp_path):
    registry, weights, metadata = good(tmp_path)
    weights.write_bytes(weights.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        verify_local(registry, "test-release", weights, metadata, check_load=True)

def test_metadata_engine_mismatch(tmp_path):
    registry, weights, metadata = good(tmp_path)
    payload = json.loads(metadata.read_text())
    payload["engine"]["actions"] += 1
    metadata.write_text(json.dumps(payload))
    registry["models"][0]["metadata"]["sha256"] = hashlib.sha256(metadata.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="engine/observation mismatch"):
        verify_local(registry, "test-release", weights, metadata)

@pytest.mark.parametrize("change,match", [
    (lambda r: r.update(champion_id="test-release"), "Champion"),
    (lambda r: r.update(latest_resumable_id="test-release"), "Latest"),
    (lambda r: r["models"].append(copy.deepcopy(r["models"][0])), "Duplicate"),
    (lambda r: r["models"][0]["weights"].update(sha256="z" * 64), "SHA256"),
    (lambda r: r["models"][0].update(parent_id="test-release"), "parent"),
    (lambda r: r["models"][0]["weights"].update(url="https://example.com/model.zip"), "URL"),
    (lambda r: r["models"][0]["verification"].update(sb3_load_checked=1), "flags"),
    (lambda r: r["models"][0].update(role="Champion"), "Champion"),
    (lambda r: r["models"][0].update(train_steps=True), "train_steps"),
])
def test_invalid_registry_rejected(tmp_path, change, match):
    registry, _, _ = good(tmp_path)
    change(registry)
    with pytest.raises(ValueError, match=match):
        validate_registry(registry)

def test_repository_registry_is_valid():
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "models/registry.json").read_text(encoding="utf-8"))
    validate_registry(registry)
    assert registry["champion_id"] is None
    assert registry["latest_resumable_id"] is None
    assert all(not row["verification"]["training_resume_checked"] for row in registry["models"])
