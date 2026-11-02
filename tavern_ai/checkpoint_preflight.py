"""Fail-closed, offline checkpoint integrity preflight.

This does NOT certify a model as resumable or competitively strong. The expected
digest must originate from a trusted, separately recorded Release/registry entry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .contract import ACTIONS, CARDS, ENGINE_HASH, FEATURES

_HEX64 = re.compile(r"[a-f0-9]{64}")
_REQUIRED = {"data", "policy.pth", "policy.optimizer.pth"}
_MAX_ARCHIVE_BYTES = 512 * 1024 * 1024


def audit_archive(archive: Path, metadata: Path, expected_sha256: str) -> dict:
    """Verify trusted digest, pinned contract, SB3 ZIP structure and CRC.

    A successful return is only *archive/metadata preflight*, not proof of
    a successful MaskablePPO.load, optimizer resume, or complete game.
    """
    archive, metadata = Path(archive), Path(metadata)
    if not isinstance(expected_sha256, str) or not _HEX64.fullmatch(expected_sha256):
        raise ValueError("Expected checkpoint SHA256 must be a lowercase 64-hex digest")
    if not archive.is_file() or not metadata.is_file():
        raise FileNotFoundError("Checkpoint archive and metadata must both exist")
    if archive.stat().st_size == 0 or archive.stat().st_size > _MAX_ARCHIVE_BYTES:
        raise ValueError("Checkpoint archive size outside bounded verification budget")
    digest = hashlib.sha256()
    with archive.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected_sha256:
        raise ValueError("Checkpoint SHA256 mismatch (refusing untrusted weights)")
    try:
        meta = json.loads(metadata.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("Checkpoint metadata is invalid JSON") from exc
    if not isinstance(meta, dict):
        raise ValueError("Checkpoint metadata must be an object")
    if type(meta.get("schema")) is not int or meta["schema"] != 1:
        raise ValueError("Unsupported checkpoint metadata schema")
    if meta.get("algorithm") != "MaskablePPO":
        raise ValueError("Unsupported checkpoint algorithm")
    steps = meta.get("total_timesteps")
    if type(steps) is not int or steps <= 0:
        raise ValueError("Missing positive integer total_timesteps")
    engine = meta.get("engine")
    if not isinstance(engine, dict):
        raise ValueError("Missing pinned TavernGym engine metadata")
    contract = {
        "version": "1.1.0", "source_hash": ENGINE_HASH,
        "features": FEATURES, "cards": CARDS, "actions": ACTIONS,
    }
    if any(engine.get(key) != value or type(engine.get(key)) is not type(value)
           for key, value in contract.items()):
        raise ValueError("Checkpoint engine/observation/action contract mismatch")
    if type(engine.get("n_cards")) is not int or engine["n_cards"] <= 0:
        raise ValueError("Missing card vocabulary size")
    try:
        with zipfile.ZipFile(archive) as zf:
            entries = zf.infolist()
            names = [item.filename for item in entries]
            if len(entries) > 64 or len(names) != len(set(names)):
                raise ValueError("Duplicated or excessive ZIP entries")
            if not _REQUIRED.issubset(set(names)):
                raise ValueError("Missing PPO model or optimizer ZIP components")
            if any(name.startswith("/") or ".." in Path(name).parts for name in names):
                raise ValueError("Unsafe ZIP entry path")
            if sum(item.file_size for item in entries) > _MAX_ARCHIVE_BYTES:
                raise ValueError("Excessive uncompressed ZIP size")
            if zf.testzip() is not None:
                raise ValueError("Checkpoint ZIP CRC validation failed")
    except (zipfile.BadZipFile, EOFError, OSError) as exc:
        raise ValueError("Corrupt checkpoint ZIP") from exc
    return {
        "schema": 1, "sha256": actual, "algorithm": "MaskablePPO",
        "total_timesteps": steps, "engine": contract,
        "archive_integrity": "passed", "model_load": "not_tested",
        "optimizer_resume": "not_tested", "complete_match": "not_tested",
        "champion_eligible": False,
    }


def probe_inference(archive: Path) -> None:
    """Optional actual engine/model inference probe; not an optimizer resume."""
    from sb3_contrib import MaskablePPO
    from .env import TavernEnv
    env = TavernEnv(seed=7819)
    try:
        model = MaskablePPO.load(str(archive), env=env, device="cpu")
        obs, _ = env.reset(seed=7819)
        mask = env.action_masks()
        action, _ = model.predict(obs, action_masks=mask, deterministic=True)
        selected = int(action)
        if selected < 0 or selected >= len(mask) or not mask[selected]:
            raise ValueError("Loaded model emitted illegal action")
        env.step(selected)
    finally:
        env.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--probe-inference", action="store_true")
    args = parser.parse_args()
    result = audit_archive(args.model, args.metadata, args.expected_sha256)
    if args.probe_inference:
        probe_inference(args.model)
        result["model_load"] = "passed"
        result["inference"] = "passed_one_action"
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
