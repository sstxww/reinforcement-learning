"""Require true discrete action IDs; never reinterpret floats, booleans or strings.

A TavernGym legal-mask membership check must refer to the action actually
selected. int(3.9) == 3 and int(True) == 1 are not valid action identities.
NumPy integer scalar actions emitted by SB3 remain valid.
"""
from __future__ import annotations

from numbers import Integral


def require_discrete_action(value: object) -> int:
    """Accept Python/NumPy integer scalars, rejecting coercion and booleans."""
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError("Action must be an integer scalar, without coercion")
    return int(value)
