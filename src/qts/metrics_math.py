"""Shared deterministic metric calculations."""

from __future__ import annotations

from collections.abc import Sequence


def max_drawdown(equity_values: Sequence[float]) -> float:
    """Return the maximum drawdown for a non-empty equity series."""

    values = tuple(equity_values)
    if not values:
        raise ValueError("equity series must not be empty")
    peak = values[0]
    drawdown = 0.0
    for equity in values:
        peak = max(peak, equity)
        if peak > 0.0:
            drawdown = min(drawdown, equity / peak - 1.0)
    return drawdown


def total_return(equity_values: Sequence[float]) -> float:
    """Return total return from first to last equity value."""

    values = tuple(equity_values)
    if not values:
        raise ValueError("equity series must not be empty")
    if values[0] == 0.0:
        raise ValueError("first equity value must not be zero")
    return values[-1] / values[0] - 1.0


__all__ = ["max_drawdown", "total_return"]
