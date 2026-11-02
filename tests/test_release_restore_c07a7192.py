"""Offline regression tests: no network, PPO or fabricated match receipt."""
import json
from pathlib import Path

import pytest

from tavern_ai import release_restore as rr

ROOT = Path(__file__).resolve().parents[1]


def registry_data():
    return json.loads((ROOT / "models/registry.json").read_text(encoding="utf-8"))


def asset_data():
    return json.loads((ROOT / "models/release_asset_digests.json").read_text(encoding="utf-8"))


def test_registered_latest_is_explicitly_unpromoted():
    data = registry_data()
    assert rr.choose_latest(data, asset_data()) == data["latest"]["id"]
    assert data["champion"] is None and data["best"] is None


def test_refuse_candidate_without_real_complete_match():
    data = registry_data()
    data["latest"]["model_full_game_passed"] = False
    with pytest.raises(ValueError, match="lineage"):
        rr.choose_latest(data, asset_data())


def test_missing_release_is_fail_closed_and_keeps_existing_checkpoint(tmp_path):
    previous = tmp_path / "protected"
    previous.mkdir()
    (previous / "model.zip").write_bytes(b"preserve")
    out = tmp_path / "checkpoints"

    def no_assets(tag, destination):
        assert tag

    with pytest.raises(FileNotFoundError, match="no fallback"):
        rr.restore(ROOT / "models/registry.json", ROOT / "models/release_asset_digests.json",
                   out, downloader=no_assets)
    assert not out.exists()
    assert (previous / "model.zip").read_bytes() == b"preserve"


def test_never_overwrites_existing_destination(tmp_path):
    out = tmp_path / "checkpoints"
    out.mkdir()
    (out / "model.zip").write_bytes(b"existing")
    with pytest.raises(FileExistsError, match="Refusing"):
        rr.restore(ROOT / "models/registry.json", ROOT / "models/release_asset_digests.json", out)
    assert (out / "model.zip").read_bytes() == b"existing"


def test_corruption_never_publishes_checkpoint(tmp_path):
    out = tmp_path / "checkpoints"

    def malicious_download(tag, destination):
        (destination / "model.zip").write_bytes(b"corrupted")
        (destination / "model.metadata.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="SHA256 mismatch"):
        rr.restore(ROOT / "models/registry.json", ROOT / "models/release_asset_digests.json",
                   out, downloader=malicious_download)
    assert not out.exists()


def test_no_automatic_random_initialization_is_present():
    workflow = (ROOT / ".github/workflows/train.yml").read_text(encoding="utf-8")
    assert "python -m tavern_ai.release_restore" in workflow
    assert "--resume checkpoints/model.zip" in workflow
    assert "initializing a fresh checkpoint" not in workflow
