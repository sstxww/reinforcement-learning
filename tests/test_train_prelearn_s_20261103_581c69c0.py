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
