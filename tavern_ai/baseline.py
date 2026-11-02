"""V1 deterministic economy-aware legal-mask baseline.

Hypothesis (not a performance claim): buying before optional ability loops and
ending the turn after a bounded number of actions improves reliability and tempo.
"""
from __future__ import annotations
import numpy as np

UPGRADE_TURNS = frozenset({2, 4, 6, 8, 10})
MAX_ACTIONS_PER_TURN = 32

class BaselinePolicy:
    def __init__(self, max_actions_per_turn: int = 36):
        if max_actions_per_turn < 1:
            raise ValueError("max_actions_per_turn must be positive")
        self.max_actions_per_turn = int(max_actions_per_turn)

    def act(self, observation: dict, context: dict | None = None) -> int:
        context = context or {}
        mask = np.asarray(observation["action_mask"], dtype=bool)
        if mask.shape != (245,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        turn = int(context.get("turn", 0))
        used = int(context.get("actions_used", 0))

        def first(lo: int, hi: int) -> int | None:
            choices = np.flatnonzero(mask[lo:hi])
            return int(choices[0] + lo) if len(choices) else None

        # Mandatory discoveries/choices must never be skipped.
        choice = first(30, 46)
        if choice is not None:
            return choice
        # A bounded action budget prevents optional actions monopolizing a turn.
        if used >= self.max_actions_per_turn and mask[0]:
            return 0
        # Play already-owned cards before buying additional minions.
        play = first(46, 126)
        if play is not None:
            return play
        # Tavern upgrade only on prespecified candidate economy turns.
        if turn in {2, 5, 7, 9, 11} and mask[3]:
            return 3
        buy = first(8, 16)
        if buy is not None:
            return buy
        # Consider optional board actions after the economy decisions.
        optional = first(126, 196)
        if optional is not None and used < self.max_actions_per_turn:
            return optional
        if mask[0]:
            return 0
        if mask[3]:
            return 3
        return int(np.flatnonzero(mask)[0])
