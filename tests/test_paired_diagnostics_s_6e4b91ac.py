"""Unit-only fake fixtures test accounting; never claim they are real game receipts."""
import hashlib
import json
from pathlib import Path

import pytest

from tavern_ai.paired_diagnostics_s_6e4b91ac import run_diagnostic, summarize


def fake_receipt(seed, policy):
    return {
        "schema": 1, "environment": "TavernGym", "agent_id": "test-session",
        "policy": policy, "seed": seed, "completed": True,
        "turns": 15, "decisions": 40,
        "engine_source_hash": "6d8712c93022ba11",
        "placements": [8, 6, 4, 2, 3, 7, 1, 5] if policy == "model"
                     else [6, 8, 4, 2, 3, 7, 1, 5],
        "truncated_combats": 0, "turn_limit_end": False,
    }


def model_fixture(tmp_path):
    model = tmp_path / "model.zip"
    model.write_bytes(b"test-only-not-a-real-PPO-checkpoint")
    return model, hashlib.sha256(model.read_bytes()).hexdigest()


def test_reports_failed_model_without_fabricated_placement(tmp_path):
    path, digest = model_fixture(tmp_path)
    def runner(seed, _agent, policy, model):
        if seed == 86410 and policy == "model":
            raise RuntimeError("Full-game safety limit exceeded")
        return fake_receipt(seed, policy)
    out = tmp_path / "diagnostics.json"
    result = run_diagnostic(path, digest, [86410, 86411], out, runner)
    assert result["summary"]["attempted_pairs"] == 2
    assert result["summary"]["complete_pairs"] == 1
    assert result["summary"]["failed_model_seeds"] == [86410]
    assert result["summary"]["unconditional_four_game_mean_is_valid"] is False
    assert result["summary"]["mean_rank_model_complete_pairs_only"] == 8
    assert result["paired"][0]["model"]["placement"] is None
    assert result["paired"][0]["model"]["receipt"] is None
    assert result["paired"][0]["baseline"]["completed"] is True
    assert json.loads(out.read_text()) == result


def test_all_failed_model_games_produce_no_rank_mean(tmp_path):
    path, digest = model_fixture(tmp_path)
    def runner(seed, _agent, policy, model):
        if policy == "model":
            raise RuntimeError("Full-game safety limit exceeded")
        return fake_receipt(seed, policy)
    res = run_diagnostic(path, digest, [9], tmp_path / "diagnostics.json", runner)
    assert res["summary"]["complete_pairs"] == 0
    assert res["summary"]["mean_rank_model_complete_pairs_only"] is None
    assert res["summary"]["champion_eligible"] is False


def test_hash_mismatch_fails_before_any_game(tmp_path):
    path, _digest = model_fixture(tmp_path)
    def never(*args):
        raise AssertionError("must not run any game")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        run_diagnostic(path, "0"*64, [1], tmp_path/"x.json", never)


def test_seed_duplicates_or_excess_count_fail(tmp_path):
    path, digest = model_fixture(tmp_path)
    with pytest.raises(ValueError, match="distinct heldout"):
        run_diagnostic(path, digest, [1, 1], tmp_path/"x.json", fake_receipt)
    with pytest.raises(ValueError, match="distinct heldout"):
        run_diagnostic(path, digest, list(range(5)), tmp_path/"x.json", fake_receipt)


def test_unknown_runtime_failure_is_not_swallowed(tmp_path):
    path, digest = model_fixture(tmp_path)
    def runner(*args):
        raise RuntimeError("unrelated simulator failure")
    with pytest.raises(RuntimeError, match="unrelated"):
        run_diagnostic(path, digest, [1], tmp_path/"x.json", runner)


def test_engine_mismatch_fails_closed(tmp_path):
    path, digest = model_fixture(tmp_path)
    def runner(seed, _agent, policy, _model):
        bad = fake_receipt(seed, policy)
        bad["engine_source_hash"] = "wrong"
        return bad
    with pytest.raises(ValueError, match="engine"):
        run_diagnostic(path, digest, [1], tmp_path/"x.json", runner)


def test_summarize_rejects_duplicate_seed():
    row={"seed":1,"model":{"completed":False,"placement":None},
         "baseline":{"completed":True,"placement":6}}
    with pytest.raises(ValueError, match="Duplicate"):
        summarize([row,row])
