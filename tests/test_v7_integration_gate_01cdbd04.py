"""Synthetic data. Not a game receipt."""
import unittest
from scripts.v7_integration_gate_01cdbd04 import audit

M = "a" * 40
H = "b" * 40

def pr():
    return {"number": 999, "state": "open", "draft": False,
            "mergeable": True, "mergeable_state": "clean",
            "base": {"ref": "main", "sha": M}, "head": {"sha": H}}

def checks():
    return {"total_count": 1, "check_runs": [{"head_sha": H,
            "name": "tests-and-full-match", "status": "completed",
            "conclusion": "success"}]}

class GateTests(unittest.TestCase):
    def check(self, p=None, c=None, main=M, head=H, reviewed=H, ancestor=True):
        return audit(p or pr(), c or checks(), main, head, reviewed, ancestor)

    def test_positive_is_not_a_merge_or_lease(self):
        result = self.check()
        self.assertEqual(result["decision"], "eligible_for_integrator")
        self.assertFalse(result["exclusive_lock_proven"])
        self.assertFalse(result["postmerge_ci_passed"])

    def test_stale_main_rejected(self):
        self.assertEqual(self.check(main="c"*40)["decision"], "blocked")

    def test_stale_head_rejected(self):
        self.assertEqual(self.check(head="c"*40)["decision"], "blocked")

    def test_unreviewed_head_rejected(self):
        self.assertEqual(self.check(reviewed="c"*40)["decision"], "blocked")

    def test_unmerged_main_rejected(self):
        self.assertEqual(self.check(ancestor=False)["decision"], "blocked")

    def test_stacked_base_rejected(self):
        p = pr(); p["base"]["ref"] = "agent/learning/v1"
        self.assertEqual(self.check(p=p)["decision"], "blocked")

    def test_draft_and_conflict_rejected(self):
        p = pr(); p["draft"] = True; p["mergeable_state"] = "dirty"
        self.assertEqual(self.check(p=p)["decision"], "blocked")

    def test_missing_or_failed_ci_rejected(self):
        for conclusion in ("failure", None):
            c = checks(); c["check_runs"][0]["conclusion"] = conclusion
            self.assertEqual(self.check(c=c)["decision"], "blocked")

    def test_ambiguous_pagination_rejected(self):
        c = checks(); c["total_count"] = 2
        self.assertEqual(self.check(c=c)["decision"], "blocked")

if __name__ == "__main__":
    unittest.main()
