"""V1 deterministic economy-first baseline with a bounded per-turn action budget."""
from __future__ import annotations
import numpy as np

MAX_ACTIONS_PER_TURN = 36

class BaselinePolicy:
    def __init__(self,max_actions_per_turn:int=MAX_ACTIONS_PER_TURN):
        if not isinstance(max_actions_per_turn,int) or max_actions_per_turn<1:
            raise ValueError("max_actions_per_turn must be a positive integer")
        self.max_actions_per_turn=max_actions_per_turn

    def act(self,observation:dict,context:dict|None=None)->int:
        context=context or {}
        mask=np.asarray(observation["action_mask"],dtype=bool)
        if mask.shape!=(245,) or not mask.any():
            raise ValueError("Expected 245-action nonempty mask")
        turn=int(context.get("turn",0))
        used=int(context.get("actions_used",0))
        if used<0:raise ValueError("Negative action count")

        def first(lo:int,hi:int)->int|None:
            xs=np.flatnonzero(mask[lo:hi])
            return int(xs[0]+lo) if len(xs) else None

        mandatory=first(30,46)
        if mandatory is not None:return mandatory
        if used>=self.max_actions_per_turn and mask[0]:return 0
        play=first(46,126)
        if play is not None:return play
        if turn in {2,5,7,9,11} and mask[3]:return 3
        buy=first(8,16)
        if buy is not None:return buy
        optional=first(126,196)
        if optional is not None:return optional
        if mask[3]:return 3
        if mask[0]:return 0
        return int(np.flatnonzero(mask)[0])
