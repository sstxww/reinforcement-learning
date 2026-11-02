"""Synthetic-only schema-2 continuation metadata regression, not model evidence."""
import json
import zipfile

import pytest

from tavern_ai.checkpoint_preflight import audit_archive
from tavern_ai.checkpoint_writer import save_checkpoint
from tavern_ai.contract import (
    ACTIONS, CARDS, ENGINE_HASH, FEATURES, CATALOG_SHA256,
    PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT,
)
from tavern_ai.train import build_checkpoint_metadata

ENGINE = {
    "version": "1.1.0", "source_hash": ENGINE_HASH,
    "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
    "n_cards": 4096,
}
COMPAT = {
    "engine": ENGINE, "catalog_sha256": CATALOG_SHA256,
    "patch_sha256": PATCH_SHA256, "ruleset_id": RULESET_ID,
    "upstream_commit": UPSTREAM_COMMIT,
}
PARENT_SHA = "a" * 64


def test_resume_preserves_schema2_compatibility_and_exact_actual_step_delta(tmp_path):
    source = {
        "schema": 2, "engine": ENGINE, "compatibility": COMPAT,
        "total_timesteps": 1280, "increment_timesteps": 1024,
    }
    meta = build_checkpoint_metadata(
        engine=ENGINE, seed=42, total_timesteps=1536,
        parent=source, parent_sha256=PARENT_SHA,
    )
    assert meta["schema"] == 2
    assert meta["increment_timesteps"] == 256
    assert meta["compatibility"] == COMPAT
    assert meta["parent_checkpoint_sha256"] == PARENT_SHA
    assert meta["total_timesteps"] == 1536

    class SyntheticZip:
        def save(self, path):
            with zipfile.ZipFile(path, "w") as zf:
                for name in ("data", "policy.pth", "policy.optimizer.pth"):
                    zf.writestr(name, b"not a real model, test fixture only")

    target = tmp_path / "child.zip"
    written = save_checkpoint(SyntheticZip(), target, meta)
    audited = audit_archive(
        target, target.with_suffix(".metadata.json"), written["checkpoint_sha256"]
    )
    assert audited["checkpoint_metadata_schema"] == 2
    assert audited["optimizer_resume"] == "not_tested"
    assert audited["champion_eligible"] is False


def test_schema1_parent_stays_schema1_with_tracked_lineage():
    meta = build_checkpoint_metadata(
        engine=ENGINE, seed=42, total_timesteps=384,
        parent={"schema": 1, "engine": ENGINE, "total_timesteps": 256},
        parent_sha256=PARENT_SHA,
    )
    assert meta["schema"] == 1
    assert meta["parent_checkpoint_sha256"] == PARENT_SHA
    assert "compatibility" not in meta


@pytest.mark.parametrize("parent", [
    {"schema": 2, "engine": ENGINE, "total_timesteps": 1280},
    {"schema": 3, "engine": ENGINE, "total_timesteps": 1280},
    {"schema": 2, "engine": ENGINE, "total_timesteps": 1280,
     "compatibility": {**COMPAT, "patch_sha256": "invalid"}},
    {"schema": 2, "engine": {**ENGINE, "actions": 244}, "total_timesteps": 1280,
     "compatibility": COMPAT},
])
def test_rejects_untrusted_schema_and_engine_instead_of_downgrading(parent):
    with pytest.raises(ValueError):
        build_checkpoint_metadata(
            engine=ENGINE, seed=42, total_timesteps=1408,
            parent=parent, parent_sha256=PARENT_SHA,
        )


def test_rejects_unbound_or_regressing_steps():
    parent = {
        "schema": 2, "engine": ENGINE, "compatibility": COMPAT,
        "total_timesteps": 1280,
    }
    for step in (0, 1279, 1280):
        with pytest.raises(ValueError):
            build_checkpoint_metadata(
                engine=ENGINE, seed=42, total_timesteps=step,
                parent=parent, parent_sha256=PARENT_SHA,
            )
    with pytest.raises(ValueError):
        build_checkpoint_metadata(
            engine=ENGINE, seed=42, total_timesteps=1408,
            parent=parent, parent_sha256=None,
        )
