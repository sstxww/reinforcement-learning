"""Two-clone local Git server exercise of task lease CAS; no external service."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v7_task_claim", ROOT / "scripts" / "v7_task_claim.py")
claim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claim)


def run(*cmd):
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()


class TestClaims(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote, self.a, self.b = root / "origin.git", root / "a", root / "b"
        run("git", "init", "--bare", str(self.remote))
        run("git", "clone", str(self.remote), str(self.a))
        run("git", "-C", str(self.a), "config", "user.name", "Agent A")
        run("git", "-C", str(self.a), "config", "user.email", "agent-a@example.invalid")
        (self.a / "README").write_text("init\n")
        run("git", "-C", str(self.a), "add", "README")
        run("git", "-C", str(self.a), "commit", "-m", "bootstrap")
        run("git", "-C", str(self.a), "push", "-u", "origin", "HEAD:refs/heads/main")
        run("git", "clone", "-b", "main", str(self.remote), str(self.b))
        run("git", "-C", str(self.b), "config", "user.name", "Agent B")
        run("git", "-C", str(self.b), "config", "user.email", "agent-b@example.invalid")
        self.original = os.getcwd()

    def tearDown(self):
        os.chdir(self.original)
        self.tmp.cleanup()

    def test_no_overwrite_release_reacquire_and_stale_sha(self):
        task = "coordination/v7-atomic-task-ref"
        a, b = "s-20261103-f6497e7a", "s-20261103-f6497e7b"
        os.chdir(self.a)
        first = claim.transition("acquire", task, a)
        self.assertEqual(first["claim"]["session_id"], a)
        os.chdir(self.b)
        with self.assertRaisesRegex(claim.ClaimError, "occupied"):
            claim.transition("acquire", task, b)
        with self.assertRaisesRegex(claim.ClaimError, "not the verified"):
            claim.transition("release", task, b)
        os.chdir(self.a)
        second = claim.transition("renew", task, a)
        self.assertNotEqual(first["sha"], second["sha"])
        with self.assertRaisesRegex(claim.ClaimError, "atomic lease rejected"):
            claim.cas_push(first["ref"], first["sha"], first["sha"], "origin")
        released = claim.transition("release", task, a)
        self.assertEqual(released["claim"]["status"], "released")
        os.chdir(self.b)
        got = claim.transition("acquire", task, b)
        self.assertEqual(got["claim"]["session_id"], b)
        self.assertEqual(claim.transition("inspect", task, b)["sha"], got["sha"])

    def test_invalid_task_owner_and_ttl(self):
        for task in ["bad", "x/../y", "x//y", "x/space here", "refs/heads/main"]:
            with self.assertRaises(claim.ClaimError):
                claim.ref_for(task)
        os.chdir(self.a)
        with self.assertRaises(claim.ClaimError):
            claim.transition("acquire", "coordination/v7-claim", "invalid")
        with self.assertRaises(claim.ClaimError):
            claim.transition("acquire", "coordination/v7-claim",
                             "s-20261103-f6497e7a", ttl_minutes=10000)


if __name__ == "__main__":
    unittest.main()
