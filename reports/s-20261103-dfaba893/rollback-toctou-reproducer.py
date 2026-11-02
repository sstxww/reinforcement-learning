"""Deterministic *synthetic* interleaving for PR #175's rollback pattern.

Does not run production restore code and does not represent a real game.
"""
from pathlib import Path
import json
import os
import tempfile


def reproduce() -> dict:
    with tempfile.TemporaryDirectory(prefix="autotavern-race-review-") as directory:
        base = Path(directory)
        stage = base / "verified.zip"
        target = base / "model.zip"
        stage.write_bytes(b"verified-by-this-restorer")
        os.link(stage, target)
        original_samefile = Path.samefile
        events = []

        def interleave_after_identity_check(self: Path, other: Path) -> bool:
            is_own_inode = original_samefile(self, other)
            events.append("samefile-returned-" + str(is_own_inode))
            if self == target and is_own_inode:
                target.unlink()
                target.write_bytes(b"concurrent-writer-checkpoint")
                events.append("other-writer-replaced-target")
            return is_own_inode

        try:
            Path.samefile = interleave_after_identity_check
            if target.samefile(stage):
                target.unlink()
                events.append("rollback-unlinked-target")
        finally:
            Path.samefile = original_samefile

        assert not target.exists(), "The interleaving must expose deletion"
        assert stage.read_bytes() == b"verified-by-this-restorer"
        return {
            "schema": 1,
            "scope": "synthetic interleaving only; not production verification or game",
            "primitive": "Path.samefile(source) followed by Path.unlink()",
            "other_writer_checkpoint_deleted": True,
            "events": events,
        }


if __name__ == "__main__":
    print(json.dumps(reproduce(), indent=2))
