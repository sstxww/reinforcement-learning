"""Pure tests; real model/game evidence is provided only by GitHub Actions."""
import pytest

from tavern_ai.action_opportunity_probe_75cf9e03 import trace


@pytest.mark.parametrize("budget", [0, -1, 101])
def test_reject_invalid_guard_budget_before_engine_load(tmp_path, budget):
    with pytest.raises(ValueError, match="max_per_turn"):
        trace(65811, tmp_path / "missing.zip", max_per_turn=budget)
