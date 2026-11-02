"""Fixture bytes test strict checks; never represent fixture as PPO evidence."""
from pathlib import Path
import copy
import hashlib
import io
import json
import zipfile

import pytest
from tavern_ai.release_asset_verifier import validate_asset_index, verify_local
from tavern_ai.contract import FEATURES, CARDS, ACTIONS, ENGINE_HASH

ROOT = Path(__file__).resolve().parents[1]
def real_index():
    return json.loads((ROOT/"models/release_asset_digests.json").read_text("utf-8"))
def canonical():
    return json.loads((ROOT/"models/registry.json").read_text("utf-8"))

def fixture(tmp_path):
    model_id = "v2-learning-41413557445"
    weights = tmp_path/"model.zip"
    # A deliberately synthetic archive: ZIP-integrity tests, not PPO inference.
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("fixture", "synthetic-checkpoint-fixture")
    weights.write_bytes(output.getvalue())
    meta = tmp_path/"model.metadata.json"
    meta.write_text(json.dumps({"algorithm":"MaskablePPO","total_timesteps":1280,"engine":{
        "version":"1.1.0","source_hash":ENGINE_HASH,"features":FEATURES,
        "cards":CARDS,"actions":ACTIONS}}))
    index = real_index()
    asset = next(a for a in index["assets"] if a["id"]==model_id)
    asset["weights"]["sha256"] = hashlib.sha256(weights.read_bytes()).hexdigest()
    candidate = next(c for c in canonical()["candidates"] if c["id"]==model_id)
    canonical_copy = canonical()
    next(c for c in canonical_copy["candidates"] if c["id"]==model_id)["checkpoint_sha256"] = asset["weights"]["sha256"]
    if canonical_copy["latest"]["id"] == model_id:
        canonical_copy["latest"]["checkpoint_sha256"] = asset["weights"]["sha256"]
    asset["metadata"]["sha256"] = hashlib.sha256(meta.read_bytes()).hexdigest()
    return index, canonical_copy, model_id, weights, meta

def test_index_matches_existing_canonical_registry():
    report = validate_asset_index(real_index(), canonical())
    assert report["canonical_candidates_matched"] >= 4
    assert report["indexed_releases"] == 7
    assert report["does_not_claim_verification"]

def test_local_good_hashes_no_fake_resume(tmp_path):
    index, canon, ident, w, m = fixture(tmp_path)
    report = verify_local(index, canon, ident, w, m)
    assert report["weight_bytes_sha256_verified"]
    assert not report["optimizer_resume_checked"]
    assert not report["complete_game_checked"]

def test_bad_weights_fail_before_loading(tmp_path):
    index, canon, ident, w, m = fixture(tmp_path)
    w.write_bytes(w.read_bytes()+b"tampering")
    with pytest.raises(ValueError,match="SHA256 mismatch"):
        verify_local(index,canon,ident,w,m,True)

def test_wrong_engine_rejected(tmp_path):
    index,canon,ident,w,m=fixture(tmp_path)
    d=json.loads(m.read_text());d["engine"]["features"]=4016
    m.write_text(json.dumps(d))
    next(a for a in index["assets"] if a["id"]==ident)["metadata"]["sha256"]=hashlib.sha256(m.read_bytes()).hexdigest()
    with pytest.raises(ValueError,match="engine/observation"):
        verify_local(index,canon,ident,w,m)

@pytest.mark.parametrize("mutation,expected", [
    ("duplicate","duplicate"),("missing","missing asset"),("mismatch","mismatch"),
    ("sha","SHA256"),("url","URL"),("bool","flag"),("bad_role","champion"),
    ("false_resume","Contradictory"),
])
def test_mutations_rejected(mutation,expected):
    index=real_index();canon=canonical()
    if mutation=="duplicate":index["assets"].append(copy.deepcopy(index["assets"][0]))
    elif mutation=="missing":index["assets"]=[a for a in index["assets"] if a["id"]!="v2-learning-41413557445"]
    elif mutation=="mismatch":index["assets"][0]["weights"]["sha256"]="a"*64
    elif mutation=="sha":index["assets"][0]["metadata"]["sha256"]="bad"
    elif mutation=="url":index["assets"][0]["weights"]["url"]="https://untrusted.invalid/x"
    elif mutation=="bool":index["assets"][0]["model_load_verified"]=1
    elif mutation=="bad_role":canon["best"]="v2-learning-41413557445"
    elif mutation=="false_resume":
        # The latest candidate has an explicitly unverified new-release resume.
        next(a for a in index["assets"] if a["id"]=="v2-learning-41413557445")["optimizer_resume_verified"]=True
    with pytest.raises(ValueError,match=expected):
        validate_asset_index(index,canon)

def test_matching_sha_does_not_bypass_zip_structure_check(tmp_path):
    index, canon, ident, w, m = fixture(tmp_path)
    w.write_bytes(b"not a valid PPO ZIP; SHA intentionally updated")
    fresh_sha = hashlib.sha256(w.read_bytes()).hexdigest()
    next(a for a in index["assets"] if a["id"] == ident)["weights"]["sha256"] = fresh_sha
    next(c for c in canon["candidates"] if c["id"] == ident)["checkpoint_sha256"] = fresh_sha
    with pytest.raises(ValueError, match="ZIP"):
        verify_local(index, canon, ident, w, m)


def test_matching_sha_does_not_bypass_member_crc_check(tmp_path):
    index, canon, ident, w, m = fixture(tmp_path)
    data = w.read_bytes()
    needle = b"synthetic-checkpoint-fixture"
    assert data.count(needle) == 1
    w.write_bytes(data.replace(needle, b"!" + needle[1:], 1))
    fresh_sha = hashlib.sha256(w.read_bytes()).hexdigest()
    next(a for a in index["assets"] if a["id"] == ident)["weights"]["sha256"] = fresh_sha
    next(c for c in canon["candidates"] if c["id"] == ident)["checkpoint_sha256"] = fresh_sha
    with pytest.raises(ValueError, match="CRC"):
        verify_local(index, canon, ident, w, m)


def test_hash_matching_unsupported_algorithm_rejected(tmp_path):
    index, canon, ident, w, m = fixture(tmp_path)
    payload = json.loads(m.read_text())
    payload["algorithm"] = "UnknownPPO"
    m.write_text(json.dumps(payload))
    next(a for a in index["assets"] if a["id"] == ident)["metadata"]["sha256"] = hashlib.sha256(m.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="algorithm"):
        verify_local(index, canon, ident, w, m)
