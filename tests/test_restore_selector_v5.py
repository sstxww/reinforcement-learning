"""Synthetic registry contracts, not model training or game evidence."""
import copy
import json
import pytest
from tavern_ai.contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES
from tavern_ai.restore_selector_v5 import RELEASE_ROOT, select_release


def registry():
    tag = "v5-verifiable-1408"
    digest = "ab" * 32
    return {
        "schema": 1, "repository": "sstxww/reinforcement-learning",
        "engine": {"version": "1.1.0", "source_hash": ENGINE_HASH,
                   "float_features": FEATURES, "card_slots": CARDS,
                   "action_count": ACTIONS},
        "latest": {"id": tag, "release_tag": tag,
                   "durable_storage": "github_release", "release": RELEASE_ROOT + tag,
                   "model_asset": "model.zip", "metadata_asset": "model.metadata.json",
                   "checkpoint_sha256": digest, "training_steps": 1408,
                   "release_download_sha256_verified": True,
                   "model_load_verified": True,
                   "real_resume_128_steps_verified": True,
                   "model_full_game_passed": True},
        "candidates": [{"id": tag, "checkpoint_sha256": digest,
                        "training_steps": 1408, "release_url": RELEASE_ROOT + tag}],
        "best": None, "champion": None,
    }


def test_accepted_catalog_does_not_claim_champion():
    selected = select_release(registry())
    assert selected == {"tag": "v5-verifiable-1408", "sha256": "ab"*32,
                        "steps": 1408, "role": "unpromoted_continuation_source"}


@pytest.mark.parametrize("mutate", [
    lambda x: x.update(schema=999),
    lambda x: x.update(repository="other/repository"),
    lambda x: x["engine"].update(source_hash="untrusted"),
    lambda x: x["latest"].update(release_tag="../bad"),
    lambda x: x["latest"].update(release="https://attacker.example/model"),
    lambda x: x["latest"].update(durable_storage="actions_artifact"),
    lambda x: x["latest"].update(metadata_asset="unknown.json"),
    lambda x: x["latest"].update(checkpoint_sha256="0"*64),
    lambda x: x["latest"].update(training_steps=0),
    lambda x: x["latest"].update(model_load_verified=False),
    lambda x: x["latest"].update(real_resume_128_steps_verified=False),
    lambda x: x["latest"].update(model_full_game_passed=False),
    lambda x: x["candidates"][0].update(checkpoint_sha256="ff"*32),
    lambda x: x.update(candidates=[]),
    lambda x: x["candidates"].append(copy.deepcopy(x["candidates"][0])),
])
def test_fail_closed_on_bad_or_ambiguous_lineage(mutate):
    data = registry()
    mutate(data)
    with pytest.raises(ValueError):
        select_release(data)


def test_json_roundtrip():
    assert select_release(json.loads(json.dumps(registry())))["steps"] == 1408
