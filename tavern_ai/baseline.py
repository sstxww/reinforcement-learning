"""Deterministic, mask-safe economy-first baseline (not a competitive policy)."""
from __future__ import annotations
import numpy as np

class BaselinePolicy:
    def __init__(self, max_actions_per_turn:int=36):
        if type(max_actions_per_turn) is not int or max_actions_per_turn<=0:
            raise ValueError("max_actions_per_turn must be a positive integer")
        self.max_actions_per_turn=max_actions_per_turn

    def act(self, observation:dict, context:dict|None=None)->int:
        context=context or {}
        mask=np.asarray(observation["action_mask"],dtype=bool)
        if mask.shape!=(245,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        turn=int(context.get("turn",0))
        used=int(context.get("actions_used",0))
        if used<0:raise ValueError("Negative action count")
        def first(lo:int,hi:int)->int|None:
            choices=np.flatnonzero(mask[lo:hi])
            return int(choices[0]+lo) if len(choices) else None

        # Resolve mandatory choice actions even if this turn used its budget.
        forced=first(30,46)
        if forced is not None:return forced
        if used>=self.max_actions_per_turn and mask[0]:return 0

        # Playing cards already in hand is normally a zero-gold prerequisite.
        play=first(46,126)
        if play is not None:return play
        # Simple scheduled tavern upgrades; do not claim optimal economics.
        if turn in {2,5,7,9,11} and mask[3]:return 3
        # Purchases take priority over discretionary rearrangement and abilities.
        buy=first(8,16)
        if buy is not None:return buy
        optional=first(126,196)
        if optional is not None:return optional
        if mask[3]:return 3
        if mask[0]:return 0
        return int(np.flatnonzero(mask)[0])
