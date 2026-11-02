"""V7 pre-compute parent-contract regression; synthetic only, no match claims."""
import pytest

from tavern_ai.contract import (
    ACTIONS, CARDS, ENGINE_HASH, FEATURES, CATALOG_SHA256,
    PATCH_SHA256, RULESET_ID, UPSTREAM_COMMIT,
)
from tavern_ai.train import preflight_resume_parent

ENGINE = {
    "version": "1.1.0", "source_hash": ENGINE_HASH,
    "features": FEATURES, "cards": CARDS, "actions": ACTIONS, "n_cards": 4096,
}
COMPAT = {
    "engine": ENGINE,
    "catalog_sha256": CATALOG_SHA256,
    "patch_sha256": PATCH_SHA256,
    "ruleset_id": RULESET_ID,
    "upstream_commit": UPSTREAM_COMMIT,
}
SHA = "a" * 64


def test_valid_schema2_parent_passes_without_training():
    parent = {"schema": 2, "engine": ENGINE, "compatibility": COMPAT,
              "total_timesteps": 1280}
    assert preflight_resume_parent(
        engine=ENGINE, parent=parent, parent_sha256=SHA
    ) is None


def test_legacy_schema1_parent_is_not_silently_downgraded():
    parent = {"schema": 1, "engine": ENGINE, "total_timesteps": 384}
    assert preflight_resume_parent(
        engine=ENGINE, parent=parent, parent_sha256=SHA
    ) is None


@pytest.mark.parametrize("parent,reason", [
    ({"schema": 2, "engine": ENGINE, "total_timesteps": 1280},
     "compatibility"),
    ({"schema": 2, "engine": ENGINE, "compatibility": {
        **COMPAT, "patch_sha256": "wrong"}, "total_timesteps": 1280},
     "compatibility"),
    ({"schema": 3, "engine": ENGINE, "total_timesteps": 1280},
     "schema"),
    ({"schema": 2, "engine": {**ENGINE, "actions": 244},
      "compatibility": COMPAT, "total_timesteps": 1280},
     "engine"),
    ({"schema": 2, "engine": ENGINE, "compatibility": COMPAT,
      "total_timesteps": True}, "step"),
    ({"schema": 2, "engine": ENGINE, "compatibility": COMPAT,
      "total_timesteps": 0}, "step"),
])
def test_invalid_parent_rejected_at_preflight_before_ppo(parent, reason):
    with pytest.raises(ValueError, match=reason):
        preflight_resume_parent(
            engine=ENGINE, parent=parent, parent_sha256=SHA
        )


def test_missing_parent_and_untrusted_digest_fail_closed():
    with pytest.raises(ValueError, match="parent"):
        preflight_resume_parent(engine=ENGINE, parent=None, parent_sha256=SHA)
    with pytest.raises(ValueError, match="digest"):
        preflight_resume_parent(
            engine=ENGINE,
            parent={"schema": 2, "engine": ENGINE, "compatibility": COMPAT,
                    "total_timesteps": 1280},
            parent_sha256="not-a-sha",
        )


def test_real_run_path_rejects_invalid_schema2_before_model_load(monkeypatch, tmp_path):
    """Synthetic caller integration, no real PPO training or match performed."""
    import hashlib
    import json
    import sys
    from types import ModuleType
    import tavern_ai.train as train

    source = tmp_path / "parent.zip"
    source.write_bytes(b"synthetic archive; this must not be deserialized")
    source.with_suffix(".metadata.json").write_text(json.dumps({
        "schema": 2,
        "engine": ENGINE,
        "compatibility": {**COMPAT, "patch_sha256": "tampered"},
        "total_timesteps": 1280,
        "checkpoint_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }), encoding="utf-8")

    calls = {"load": 0, "closed": 0}

    class StubEnv:
        def __init__(self, seed): self.seed = seed
        def close(self): calls["closed"] += 1

    class StubPPO:
        @staticmethod
        def load(*args, **kwargs):
            calls["load"] += 1
            raise AssertionError("MaskablePPO.load must not run on invalid parent")

    sb3 = ModuleType("sb3_contrib")
    sb3.MaskablePPO = StubPPO
    model = ModuleType("tavern_ai.model")
    model.TavernExtractor = object
    monkeypatch.setitem(sys.modules, "sb3_contrib", sb3)
    monkeypatch.setitem(sys.modules, "tavern_ai.model", model)
    monkeypatch.setattr(train, "verify_engine", lambda: ENGINE)
    monkeypatch.setattr(train, "TavernEnv", StubEnv)
    with pytest.raises(ValueError, match="compatibility"):
        train.run(128, 42, tmp_path / "child.zip", resume=source)
    assert calls == {"load": 0, "closed": 1}
