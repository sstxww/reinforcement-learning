"""No simulator is mocked as real; these are contract mutation tests only."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

SRC = Path(__file__).resolve().parents[1] / "scripts" / "v7_candidate_censor_audit_4c5fcc9a.py"
spec = importlib.util.spec_from_file_location("censor_audit", SRC)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
P = "a" * 64
C = "b" * 64
F = "c" * 64


def sample():
    def game(policy, seed, rank, sha):
        return {"environment": "TavernGym", "completed": True, "policy": policy,
                "engine_version": "1.1.0", "engine_source_hash": "6d8712c93022ba11",
                "placements": [rank] + [i for i in range(1, 9) if i != rank],
                "seed": seed, "decisions": 50, "truncated_combats": 0,
                "turn_limit_end": False, "model_sha256": sha}
    return dict(baseline=game("baseline", 97303, 5, None),
                parent=game("model", 97303, 8, P),
                candidate=game("model", 97304, 8, C),
                manifest={"parent_sha256": P, "candidate_sha256": C,
                          "training_steps_total": 1536, "training_steps_added": 128,
                          "storage": {"durable": False}},
                failure={"parent_sha256": P, "candidate_sha256": F,
                         "candidate_training_steps": 1536,
                         "candidate_heldout": {"completed_report": False, "any_placement_claimed": False,
                                               "error": "Full-game safety limit exceeded",
                                               "requested_seeds": [932040, 932041]}})


def test_distinct_cohorts_and_censored_rank_never_eight():
    report = a.audit(**sample())
    assert report["matched_parent_baseline"]["parent_minus_baseline"] == 3
    assert report["cohorts"][0]["rank"] == 8
    assert report["cohorts"][1]["heldout_rank"] is None
    assert report["combined_candidate_mean_rank"] is None
    assert report["verified_candidate_improvement"] is False


@pytest.mark.parametrize("change", [
    lambda x: x["failure"].update(candidate_sha256=C),
    lambda x: x["failure"]["candidate_heldout"].update(any_placement_claimed=True),
    lambda x: x["failure"]["candidate_heldout"].update(completed_report=True),
    lambda x: x["candidate"].update(model_sha256=P),
    lambda x: x["candidate"].update(completed=False),
    lambda x: x["candidate"].update(truncated_combats=1),
    lambda x: x["candidate"].update(guard_forced_ends=1),
    lambda x: x["parent"].update(seed=7),
    lambda x: x["manifest"]["storage"].update(durable=True),
    lambda x: x["candidate"].update(placements=[8] * 8),
    lambda x: x["parent"].update(model_guard_forced_end=2),
])
def test_fail_closed_for_identity_assistance_and_incomplete(change):
    records = deepcopy(sample())
    change(records)
    with pytest.raises(ValueError):
        a.audit(**records)
