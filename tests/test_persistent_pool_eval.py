"""Round 002 bounded process-pool evaluation tests."""
import pytest
import tavern_ai.persistent_pool_eval as mod

def test_batches_are_bounded_nonoverlapping_and_seeded():
    batches = mod.make_batches(28801)
    assert len(batches) == 4
    assert all(len(x) == 16 for x in batches)
    assert batches[0][0] == 28801 and batches[-1][-1] == 28864
    assert len({s for batch in batches for s in batch}) == 64

def test_negative_seeds_rejected():
    with pytest.raises(ValueError, match="negative"):
        mod.make_batches(-1)

def test_modes_are_restricted():
    with pytest.raises(ValueError, match="Unknown execution mode"):
        mod.run_mode(mod.make_batches(28801), "test", "unknown")

def test_fixed_batch_sizes_enforced():
    with pytest.raises(ValueError, match="four fixed"):
        mod.run_mode([[1]], "test", "serial")

def test_serial_runner_preserves_input_order(monkeypatch):
    def fake_worker(task):
        seed, agent_id = task
        return {"pid": 321, "receipt": {"seed": seed, "agent_id": agent_id}}
    monkeypatch.setattr(mod, "_worker", fake_worker)
    result = mod.run_mode(mod.make_batches(28801), "test", "serial")
    assert len(result["records"]) == 64
    assert [r["seed"] for r in result["records"]] == list(range(28801, 28865))
    assert result["worker_pids"] == [321]
    assert result["elapsed_seconds"] >= 0
