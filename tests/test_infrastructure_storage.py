from pathlib import Path
import hashlib
import json
import pytest
from scripts.cleanup_generated import clean
from scripts.candidate_release import inspect_candidate

def test_cleanup_only_discards_caches(tmp_path):
    for name in ("checkpoints", "experiments", "reports", "models", "vendor"):
        protected = tmp_path / name / "__pycache__"
        protected.mkdir(parents=True)
        (protected / "keep.pyc").write_bytes(b"keep")
    scratch = tmp_path / "tavern_ai" / "__pycache__"
    scratch.mkdir(parents=True)
    (scratch / "old.pyc").write_bytes(b"x")
    matches = clean(tmp_path, apply=True)
    assert scratch in matches and not scratch.exists()
    assert (tmp_path / "checkpoints" / "__pycache__" / "keep.pyc").exists()
    assert (tmp_path / "experiments" / "__pycache__" / "keep.pyc").exists()

def test_candidate_rejects_hash_mismatch(tmp_path):
    model = tmp_path / "model.zip"
    model.write_bytes(b"dummy test bytes, never an actual checkpoint")
    meta = tmp_path / "model.metadata.json"
    meta.write_text(json.dumps({"checkpoint_sha256": "0"*64,
                                "engine": {"version": "1.1.0",
                                           "source_hash": "6d8712c93022ba11"},
                                "compatibility": {"engine": {}},
                                "total_timesteps": 128}))
    receipt = tmp_path / "receipt.json"
    receipt.write_text("{}")
    evaluation = tmp_path / "eval.json"
    evaluation.write_text("{}")
    with pytest.raises(ValueError, match="Model hash"):
        inspect_candidate(model, meta, receipt, evaluation)
